from typing import Annotated
from dataclasses import dataclass
from ..interfaces import FancyHelloABC, IHello, ILucky, ISettings
from ..servicetools import wired_service, Wired


@wired_service(FancyHelloABC)
@dataclass
class FancyHelloService(FancyHelloABC):
    hello_api: Annotated[IHello, Wired]
    lucky_api: Annotated[ILucky, Wired]
    prefix: Annotated[str, Wired(iface=ISettings, key='hello.prefix')]
    suffix: str = 'And good day to you!'

    def get_lucky_number(self):
        return f"Your lucky number is {self.lucky_api.get_lucky_number()}."

    def hello(self, name: str):
        return ' '.join([
            self.prefix,
            self.hello_api.hello(name=name),
            self.get_lucky_number(),
            self.suffix,
        ])
