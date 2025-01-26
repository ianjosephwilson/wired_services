from typing import Protocol
from wired import ServiceContainer
from typing import Callable, Any


class DependencyResolverProtocol(Protocol):

    def resolve_dependencies(self, service_factory: Callable, container: ServiceContainer) -> dict[str, Any]:
        return {}
