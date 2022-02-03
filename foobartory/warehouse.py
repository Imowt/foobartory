from typing import TYPE_CHECKING, List

from pydantic import BaseModel

from foobartory.models.items.bar import Bar
from foobartory.models.items.foo import Foo
from foobartory.models.items.foobar import FooBar

if TYPE_CHECKING:
    from foobartory.models.robot.robot import Robot


class WareHouse(BaseModel):
    balance: float

    robots: List["Robot"]
    bars: List[Bar]
    foos: List[Foo]
    foobars: List[FooBar]
