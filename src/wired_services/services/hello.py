from typing import Annotated

from ..servicetools import wired_service, Wired
from ..interfaces import INow, ISettings, IHello, IHelloAgain


@wired_service(IHello)
class HelloService:

    now_api: Annotated[INow, Wired]

    def __init__(self, now_api: INow):
        self.now_api = now_api

    def hello(self, name: str|None=None):
        if not name:
            name = 'there'
        return f'Hello {name}, the date and time is {self.now_api.get_local_now().isoformat()}.'


@wired_service(IHelloAgain)
class HelloAgainService(HelloService):

    def hello(self, name: str|None=None):
        if not name:
            name = 'there'
        return f'Hello again {name}, the date and time is {self.now_api.get_local_now().isoformat()}.'
