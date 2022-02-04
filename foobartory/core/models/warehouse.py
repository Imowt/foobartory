from typing import TYPE_CHECKING, List

from pydantic import BaseModel

from foobartory.core.models.items.bar import Bar
from foobartory.core.models.items.foo import Foo
from foobartory.core.models.items.foobar import FooBar

if TYPE_CHECKING:
    from foobartory.core.robot import Robot


class Warehouse(BaseModel):
    """
    Object containing all the datas that has to be shared between the Factory and the Robots
    """
    balance: float = 0
    robots: List["Robot"] = []
    bars: List[Bar] = []
    foos: List[Foo] = []
    foobars: List[FooBar] = []
