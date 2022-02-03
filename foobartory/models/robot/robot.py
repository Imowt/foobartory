import random
import time
from threading import Thread, Lock, Event
from typing import List, Dict, Callable

from foobartory.models.items.bar import Bar
from foobartory.models.items.foo import Foo
from foobartory.models.items.foobar import FooBar
from foobartory.models.robot.enums.robot_action import RobotActivity
from foobartory.settings.settings import settings

ROBOT_LOCK = Lock()


class Robot(Thread):
    def __init__(
        self,
        id: int,
        money: float,
        foos: List[Foo],
        bars: List[Bar],
        foobars: List[FooBar],
        robots: List["Robot"],
        finished: Event,
    ):
        super().__init__()
        self.daemon = True
        self.id: int = id
        self.money: float = money
        self.foos: List[Foo] = foos
        self.bars: List[Bar] = bars
        self.foobars: List[FooBar] = foobars
        self.robots: List["Robot"] = robots
        self.stop_event: Event = finished
        self.activity: RobotActivity = RobotActivity.MINING_FOO
        self.activities: Dict[RobotActivity, Callable] = {
            RobotActivity.BUYING_ROBOT: self.buy_robot,
            RobotActivity.MINING_FOO: self.mine_foo,
            RobotActivity.MINING_BAR: self.mine_bar,
            RobotActivity.SELLING_FOOBARS: self.selling_foobars,
            RobotActivity.ASSEMBLING_FOOBAR: self.assemble_foobar,
        }

    def run(self):
        """
        Starts the robot thread
        :return:
        """
        while not self.stop_event.is_set():
            self.execute_next_action()

    def execute_next_action(self):
        """
        Return the new action and check if it's still valid due to the moving duration
        :return:
        """
        next_action: RobotActivity = self.get_next_action()
        if next_action != self.activity:
            self.move()
        if self.stop_event:
            return
        elif next_action == self.get_next_action():
            self.activity = next_action
            self.execute_action()
        else:
            self.execute_next_action()

    def execute_action(self):
        """
        Execute the current action
        :return:
        """
        self.activities.get(self.activity)()

    def move(self):
        """
        Robot is moving to a new activity
        :return:
        """
        self.__wait(settings.ROBOT_MOVING_DURATION)

    def get_next_action(self) -> RobotActivity:
        """
        Returns the robot next action
        :return: robot next action
        """
        if self.can_buy_robot():
            return RobotActivity.BUYING_ROBOT
        elif self.can_sell_foobars():
            return RobotActivity.SELLING_FOOBARS
        elif self.can_assemble_foobar():
            return RobotActivity.ASSEMBLING_FOOBAR
        elif len(self.foos) <= settings.ROBOT_FOO_COST:
            return RobotActivity.MINING_FOO
        else:
            return RobotActivity.MINING_BAR

    def __wait(self, seconds: float) -> None:
        """
        Make the robot to wait for seconds
        :param seconds: time to wait
        :return:
        """
        time.sleep(seconds * settings.TIME_RATIO)

    def mine_foo(self) -> None:
        """
        Mine foo
        :return:
        """
        self.__wait(settings.ROBOT_MINING_FOO_DURATION)
        self.foos.append(Foo())

    def mine_bar(self) -> None:
        """
        Mine bar
        :return:
        """
        self.__wait(random.uniform(settings.ROBOT_MINING_BAR_DURATION_MIN, settings.ROBOT_MINING_BAR_DURATION_MAX))
        self.bars.append(Bar())

    def can_assemble_foobar(self) -> bool:
        """
        If it can assemble a new foobar
        :return: bool
        """
        return len(self.foos) > 0 and len(self.bars) > 0

    def assemble_foobar(self, success_rate: float = settings.ROBOT_ASSEMBLING_FOOBAR_SUCCESS_RATE) -> None:
        """
        Assemble a foobar
        :param success_rate: assembly success rate
        :return:
        """
        bar: Bar = self.bars.pop(0)
        foo: Foo = self.foos.pop(0)
        self.__wait(settings.ROBOT_ASSEMBLING_FOOBAR_DURATION)
        if random.randrange(100) < success_rate:  # Success
            self.foobars.append(FooBar(foo=foo, bar=bar))
        else:  # Fail
            self.bars.append(bar)

    def can_sell_foobars(self) -> bool:
        """
        Returns if the robot can sell foobars
        :return: if we can sell foobars
        """
        return len(self.foobars) > 0

    def get_foobars_to_sell(self) -> List[FooBar]:
        """
        Returns the maximum foobars to sell
        :return: foobars to sell
        """
        foobars_number: int = min(len(self.foobars), settings.ROBOT_SELLING_FOOBARS_MAX)
        return [self.foobars.pop(0) for _ in range(foobars_number)]

    def selling_foobars(self) -> None:
        """
        Sell foobars
        :return:
        """
        foobars: List[FooBar] = self.get_foobars_to_sell()
        self.__wait(settings.ROBOT_SELLING_FOOBARS_DURATION)
        self.money += settings.FOOBAR_VALUE * len(foobars)
        print("SELLING FOOBARS", self.money, settings.FOOBAR_VALUE, len(foobars))

    def can_buy_robot(self) -> bool:
        """
        If we can buy a new robot
        :return: bool
        """
        return self.money > settings.ROBOT_COST and len(self.foos) > settings.ROBOT_FOO_COST

    def buy_robot(self) -> None:
        """
        Buy a new robot
        :return:
        """
        self.money -= settings.ROBOT_COST
        self.foos = self.foos[settings.ROBOT_FOO_COST :]
        self.robots.append(
            Robot(
                id=len(self.robots) + 1,
                money=self.money,
                foos=self.foos,
                bars=self.bars,
                foobars=self.foobars,
                robots=self.robots,
            )
        )
