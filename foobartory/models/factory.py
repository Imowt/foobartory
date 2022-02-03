import time
from threading import Thread, Event

from foobartory.models.items.bar import Bar
from foobartory.models.items.foo import Foo
from foobartory.models.items.foobar import FooBar
from foobartory.models.monitor import Monitoring
from foobartory.models.robot.robot import Robot
from foobartory.settings.settings import settings


class Factory:
    def __init__(self):
        self.money: float = 0
        self.foos: list[Foo] = []
        self.bars: list[Bar] = []
        self.foobars: list[FooBar] = []
        self.robots: list[Robot] = []
        self.stop_event: Event = Event()
        self.init_default_robots()
        self.monitoring_thread = Thread(
            target=Monitoring.print_state,
            args=(
                self.money,
                self.foos,
                self.bars,
                self.foobars,
                self.robots,
                self.stop_event,
            ),
        )

    def init_default_robots(self):
        """
        Initialize the default robots
        :return:
        """
        for _ in range(settings.DEFAULT_ROBOTS):
            robot: Robot = Robot(
                id=len(self.robots) + 1,
                money=self.money,
                foos=self.foos,
                bars=self.bars,
                foobars=self.foobars,
                robots=self.robots,
                finished=self.stop_event,
            )
            self.robots.append(robot)
            robot.start()

    def run(self) -> None:
        """
        Manage the factory run
        :return:
        """
        self.monitoring_thread.start()
        while len(self.robots) < settings.MAX_ROBOTS:
            pass
        self.stop_event.set()
