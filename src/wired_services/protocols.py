from typing import Protocol
from wired import ServiceContainer
from typing import Callable, Any


class WiredMarkerProtocol(Protocol):
    pass


class DependencyExtractorProtocol(Protocol):

    def extract(self, service_factory: Callable) -> dict[str, WiredMarkerProtocol]:
        return {}


class DependencyResolverProtocol(Protocol):

    def resolve(self, container: ServiceContainer, dep_specs: dict[str, WiredMarkerProtocol]) -> dict[str, Any]:
        return {}
