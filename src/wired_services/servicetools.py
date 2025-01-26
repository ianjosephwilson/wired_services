"""
Design notes
++++++++++++

Default handling
----------------
- Using default and default_factory for failed service resolution seems
  to be a very exceptional case that could be handled in the service itself.
- Using default/default_factory for post service resolution, ie. for getattr or [] seems
  to be a common case, ie. get this setting unless it is missing then use this default.
- I'm not convinced using it for getattr is actually a good idea either though.
"""
from dataclasses import dataclass, is_dataclass, field
from typing import Any, get_origin, get_args, Annotated, get_type_hints
from inspect import get_annotations, isclass
from venusian import attach as venusian_attach
from .protocols import DependencyResolverProtocol


@dataclass
class Wired:
    iface: Any|None = None
    name: str|None = None
    context: Any|None = None
    attr: str|None = None
    key: str|None = None
    call_args: list|None = None
    call_kwargs: dict|None = None


@dataclass
class AnnotatedDependencyResolver:
    """
    Resolve dependencies from annotations of service factory.

    spec_class:
        The class to use to specify where/how to load a dependency within Annotated.
    """
    spec_class: type = Wired

    def create_empty_spec(self):
        # To support Annotated[iface, Wired] in a streamlined way we just make an empty
        # Wired as if the specification was Annotated[iface, Wired()].
        return self.spec_class()

    def resolve_dependencies(self, service_factory, container):
        """
        Resolve dependencies that should be injected into the service's factory.

        service_factory: callable
          The factory we extract the dependency specifications from to resolve the dependencies.
        container:
          Wired container to get actual services from.

        return: dict[str, Any]
          Return a mapping from arg/property to resolved dependency.
        """
        deps = {}
        hints = get_type_hints(service_factory, include_extras=True)
        for k, hint in hints.items():
            origin = get_origin(hint)
            if origin is Annotated:
                a_args = get_args(hint)
                iface = a_args[0]
                for a_arg in a_args[1:]:
                    spec = None
                    if isinstance(a_arg, self.spec_class):
                        # ie. Annotated[IFace, Wired(...)] or Annotated[IFace, Wired()]
                        spec = a_arg
                    elif isclass(a_arg) and issubclass(a_arg, self.spec_class):
                        # ie. Annotated[IFace, Wired]
                        spec = self.create_empty_spec()

                    if spec:
                        # Override hint's type if spec provides alternative iface.
                        if spec.iface is not None:
                            iface = spec.iface
                        result = container.get(iface, name=spec.name or '')
                        # Interact with the service to get the final dependency if needed.
                        if spec.attr:
                            result = getattr(result, spec.attr)
                        if spec.key:
                            result = result[spec.key]
                        if spec.call_kwargs or spec.call_args:
                            call_kwargs = spec.call_kwargs or {}
                            call_args = spec.call_args or ()
                            result = result(*call_args, **call_kwargs)
                        deps[k] = result
        return deps

T = TypeVar('T')

@dataclass
class Injector:
    """
    Wrap a service factory and invoke it to create the service when requested.

    service_factory:
      The factory to inject dependencies into to create service.

    factory_kwargs:
      Dict of kwargs used as defaults for factory.
      Any resolved dependencies take precendence over these kwargs.
      These allow us to partially preconfigure a service at definition time but
      plug in the dynamic parts when factory is called.

    resolver:
      The resolver to use to resolve dependencies.
    """

    service_factory: Type[T]|Callable[...,T]
    factory_kwargs: dict[str, Any] = field(default_factory=dict)
    resolver: DependencyResolverProtocol = field(default_factory=AnnotatedDependencyResolver)

    def __call__(self, container) -> T:
        return self.service_factory(
            **dict(
                self.factory_kwargs,
                **self.resolver.resolve_dependencies(
                    self.service_factory, container
                ),
            )
        )


def wired_service(
    iface=None,
    context=None,
    name="",
    category="wired_service",
    injector_factory=Injecter,
    **injector_factory_kwargs,
):
    """
    Handle registration of a service class's factory in the registry.

    iface:
      Register for this iface.
    context:
      Register for this context.
    name:
      Register for this name.
    category:
      Category to attach venusian callback to.
    injector_factory:
      Build a factory around the wrapped factory that can inject dependencies.
    injector_factory_kwargs:
      Extra kwargs to pass through to injector factory.
    """

    def wrapper(service_factory):
        def callback(scanner, cls_name, cls):
            """Callback for venusian scan."""
            registry = scanner.registry
            injector = injector_factory(service_factory, **injector_factory_kwargs)
            registry.register_factory(injector, iface, context=context, name=name)

        venusian_attach(service_factory, callback, category=category)
        return service_factory

    return wrapper


# @TODO: Not sure what would be the proper way to type this
# or the best way to manage something like this.
def wired_value(
    iface=None,
    context=None,
    name="",
    category="wired_service",
):
    """
    Wrap a single non-primitive value in a factory that just returns it.

    This could be fixed function or class to be shared with no factory invocations.
    """
    def wrapper(value: Union[Type[T]|Callable]):
        def callback(scanner, cls_name, cls):
            """Callback for venusian scan."""
            registry = scanner.registry
            registry.register_factory(lambda container: value, iface, context=context, name=name)

        venusian_attach(value, callback, category=category)
        return value

    return wrapper
