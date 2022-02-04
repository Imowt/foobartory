import random
import time
from threading import Thread, Event
from typing import List, TYPE_CHECKING

from foobartory.core.models.items.bar import Bar
from foobartory.core.models.items.foo import Foo
from foobartory.core.models.items.foobar import FooBar
from foobartory.core.models.robot.enums.robot_action import RobotActivity
from foobartory.settings.settings import settings

if TYPE_CHECKING:
    from foobartory.core.models.warehouse import Warehouse


class Robot(Thread):
    def __init__(self, robot_id: int, warehouse: "Warehouse", stop_event: Event):
        super().__init__()
        self.daemon = True
        self.id: int = robot_id
        self.warehouse: "Warehouse" = warehouse
        self.stop_event: Event = stop_event
        self.activity: RobotActivity = RobotActivity.MINING_FOO

    def run(self) -> None:
        """
        Robot thread robot entrypoint
        :return:
        """
        while not self.stop_event.is_set():
            self.execute_next_activity()

    def execute_next_activity(self) -> None:
        """
        Return the new action and check if it's still valid due to the moving duration
        :return:
        """
        next_activity: RobotActivity = self.get_next_activity()
        if next_activity != self.activity:
            self.move()
        if self.stop_event.is_set():
            return
        if (
            next_activity == self.get_next_activity()
        ):  # Check again to be sure that the activity is still valid after the movement duration
            self.activity = next_activity
            self.execute_activity()
        else:
            self.execute_next_activity()

    def get_next_activity(self) -> RobotActivity:
        """
        Returns the robot next action
        :return: robot next action
        """
        if self.can_buy_robot():
            return RobotActivity.BUYING_ROBOT
        elif self.has_enough_balance_to_buy_robot():
            return RobotActivity.MINING_FOO
        elif self.can_sell_foobars():
            return RobotActivity.SELLING_FOOBARS
        elif self.can_assemble_foobar():
            return RobotActivity.ASSEMBLING_FOOBAR
        elif not self.has_enough_foo_to_buy_robot():
            return RobotActivity.MINING_FOO
        else:
            return RobotActivity.MINING_BAR

    def execute_activity(self) -> None:
        """
        Execute the current action
        :return:
        """
        if self.activity == RobotActivity.BUYING_ROBOT:
            self.buy_robot()
        elif self.activity == RobotActivity.ASSEMBLING_FOOBAR:
            self.assemble_foobar()
        elif self.activity == RobotActivity.MINING_BAR:
            self.mine_bar()
        elif self.activity == RobotActivity.SELLING_FOOBARS:
            self.sell_foobars()
        else:
            self.mine_foo()

    def wait(self, seconds: float) -> None:
        """
        Make the robot to wait for seconds
        :param seconds: time to wait
        :return:
        """
        time.sleep(seconds * settings.TIME_RATIO)

    def move(self) -> None:
        """
        Robot is moving to a new activity
        :return:
        """
        self.wait(settings.ROBOT_MOVING_DURATION)

    def mine_foo(self) -> None:
        """
        Mine foo
        :return:
        """
        self.wait(settings.ROBOT_MINING_FOO_DURATION)
        self.warehouse.foos.append(Foo())

    def mine_bar(self) -> None:
        """
        Mine bar
        :return:
        """
        self.wait(random.uniform(settings.ROBOT_MINING_BAR_DURATION_MIN, settings.ROBOT_MINING_BAR_DURATION_MAX))
        self.warehouse.bars.append(Bar())

    def can_assemble_foobar(self) -> bool:
        """
        If it can assemble a new foobar
        :return: bool
        """
        return len(self.warehouse.foos) > 0 and len(self.warehouse.bars) > 0

    def assemble_foobar(self, success_rate: float = settings.ROBOT_ASSEMBLING_FOOBAR_SUCCESS_RATE) -> None:
        """
        Assemble a foobar
        :param success_rate: assembly success rate
        :return:
        """
        bar: Bar = self.warehouse.bars.pop(0)
        foo: Foo = self.warehouse.foos.pop(0)
        self.wait(settings.ROBOT_ASSEMBLING_FOOBAR_DURATION)
        if random.randrange(100) < success_rate:  # Success
            self.warehouse.foobars.append(FooBar(foo=foo, bar=bar))
        else:  # Fail
            self.warehouse.bars.append(bar)

    def can_sell_foobars(self) -> bool:
        """
        Returns if the robot can sell foobars
        :return: if we can sell foobars
        """
        return len(self.warehouse.foobars) > settings.ROBOT_SELLING_FOOBARS_MIN

    def get_foobars_to_sell(self) -> List[FooBar]:
        """
        Returns the maximum foobars to sell
        :return: foobars to sell
        """
        foobars_number: int = min(len(self.warehouse.foobars), settings.ROBOT_SELLING_FOOBARS_MAX)
        return [self.warehouse.foobars.pop(0) for _ in range(foobars_number)]

    def sell_foobars(self) -> None:
        """
        Sell foobars
        :return:
        """
        foobars: List[FooBar] = self.get_foobars_to_sell()
        self.wait(settings.ROBOT_SELLING_FOOBARS_DURATION)
        self.warehouse.balance += settings.FOOBAR_VALUE * len(foobars)

    def can_buy_robot(self) -> bool:
        """
        If we can buy a new robot
        :return: bool
        """
        return self.has_enough_balance_to_buy_robot() and self.has_enough_foo_to_buy_robot()

    def has_enough_balance_to_buy_robot(self) -> bool:
        """
        Returns if it has enough balance to buy a new robot
        :return: bool
        """
        return self.warehouse.balance >= settings.ROBOT_COST

    def has_enough_foo_to_buy_robot(self) -> bool:
        """
        Returns if it has enough foos to buy a new robot
        :return: bool
        """
        return len(self.warehouse.foos) >= settings.ROBOT_FOO_COST

    def buy_robot(self) -> None:
        """
        Buy a new robot
        :return:
        """
        self.warehouse.balance -= settings.ROBOT_COST
        self.warehouse.foos = self.warehouse.foos[settings.ROBOT_FOO_COST:]
        new_robot: Robot = Robot(
            robot_id=len(self.warehouse.robots) + 1, warehouse=self.warehouse, stop_event=self.stop_event
        )
        self.warehouse.robots.append(new_robot)
        new_robot.start()
