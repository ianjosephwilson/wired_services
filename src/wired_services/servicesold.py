""" Sample services. """
from datetime import datetime, timezone, timedelta
from typing import Annotated

from .interfaces import INow, IHello, IPersonalHello, CoolHelloABC, AllHelloABC, ISettings
from .servicetools import wired_service, Wired




class PersonalHelloService:
    """ Ex 1-dep, factory: We are in the factory business now. """
    def __init__(self, hello_api):
        self.hello_api = hello_api

    def hello(self, name):
        # Welcome... to... Enterprise!!!
        hello_text = self.hello_api.hello()
        return f'Hello there {name},' + hello_text.split(',', 1)[1]

@wired_service(IPersonalHello, wrap_in_dataclass=False)
def build_personal_hello(hello_api: Annotated[IHello, Wired]):
    return PersonalHelloService(hello_api=hello_api)


@wired_service(CoolHelloABC, wrap_in_dataclass=False)
class CoolHelloService(CoolHelloABC):

    def hello(self):
        return f'Hey fam.'


@wired_service(AllHelloABC, wrap_in_dataclass=True)
class AllHelloService(AllHelloABC):
    """
    Good bye constructors! Good bye factories!
    """
    hello_api: Annotated[IHello, Wired]
    personal_hello_api: Annotated[IPersonalHello, Wired]
    cool_hello_api: Annotated[CoolHelloABC, Wired]
    # Load from iface but just take out key, this prevents
    # coupling of entire settings to service instead of a single
    # setting.
    prefix: Annotated[str, Wired(iface=ISettings, key='hello.prefix')]

    # This is just a plain property that goes about its merry day undisturbed.
    suffix: str = 'And good day to you!'

    def hello(self, name):
        return ' '.join([
            self.prefix,
            self.hello_api.hello(),
            self.personal_hello_api.hello(name),
            self.cool_hello_api.hello(),
            self.suffix,
        ])

# The alternative way using exclusively dataclasses.
'''
@wired_service(AllHelloABC, wrap_in_dataclass=False)
class AllHelloService2(AllHelloABC):
    hello_api: IHello
    personal_hello_api: IPersonalHello
    cool_hello_api: CoolHelloABC
    # Load from iface but just take out key, this prevents
    # coupling of entire settings to service instead of a single
    # setting.
    prefix: str = wired_field(ISettings, key='hello.prefix')

    # This is just a plain property that goes about its merry day undisturbed.
    suffix: str = 'And good day to you!'

    def hello(self, name):
        return ' '.join([
            self.prefix,
            self.hello_api.hello(),
            self.personal_hello_api.hello(name),
            self.cool_hello_api.hello(),
            self.suffix,
        ])
'''
