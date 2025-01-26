from zope.interface import Interface
from abc import ABC


class INow(Interface):
    pass


class IHello(Interface):
    pass


class IHelloAgain(Interface):
    pass


class ILucky(Interface):
    pass


class FancyHelloABC(ABC):
    pass


class ISettings(Interface):
    pass
