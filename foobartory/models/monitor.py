import time
from threading import Thread, Event
from typing import List

from foobartory.models.items.bar import Bar
from foobartory.models.items.foo import Foo
from foobartory.models.items.foobar import FooBar
from foobartory.settings.settings import settings


class Monitoring(Thread):
    @staticmethod
    def print_state(
        money: float,
        foos: List[Foo],
        bars: List[Bar],
        foobars: List[FooBar],
        robots: List["Robot"],
        stop_event: Event,
    ) -> None:
        """
        Print the current state
        :return:
        """
        while not stop_event.is_set():
            print("-" * 30)
            print(f"money: {money}")
            print(f"robots:{len(robots)}")
            print(f"foobars: {len(foobars)}")
            print(f"foos: {len(foos)}")
            print(f"bars: {len(bars)}")
            print(stop_event.is_set())
            time.sleep(settings.MONITORING_REFRESH_RATE * settings.TIME_RATIO)
