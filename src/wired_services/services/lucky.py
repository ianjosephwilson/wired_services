from dataclasses import dataclass
from random import randint
from typing import Annotated

from ..servicetools import wired_service, Wired
from ..interfaces import ILucky, ISettings


@dataclass
class LuckyService:

    max_number: int

    def get_lucky_number(self):
        return randint(1, self.max_number)


max_number_dep = Annotated[int, Wired(ISettings, key='hello.lucky_max_number')]


@wired_service(ILucky)
def build_lucky_service(max_number: max_number_dep):
    return LuckyService(max_number=max_number)
