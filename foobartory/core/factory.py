import time
from threading import Thread, Event

from foobartory.core.models.warehouse import Warehouse
from foobartory.core.robot import Robot
from foobartory.settings.settings import settings


class Factory:
    def __init__(self):
        super().__init__()
        self.warehouse: Warehouse = Warehouse()
        self.stop_event: Event = Event()
        self.init_default_robots()
        self.monitoring_thread: Thread = Thread(target=self.print_state_monitoring, daemon=True)

    def init_default_robots(self):
        """
        Initialize the default robots
        :return:
        """
        for _ in range(settings.DEFAULT_ROBOTS):
            robot: Robot = Robot(
                robot_id=len(self.warehouse.robots) + 1, warehouse=self.warehouse, stop_event=self.stop_event
            )
            self.warehouse.robots.append(robot)
            robot.start()

    def run(self) -> None:
        """
        Manage the factory run
        :return:
        """
        self.monitoring_thread.start()
        while len(self.warehouse.robots) < settings.MAX_ROBOTS:
            pass
        self.stop_event.set()
        self.print_state()

    def print_state(self) -> None:
        """
        Print the current state
        :return:
        """
        print("-" * 30)
        print(f"robots:{len(self.warehouse.robots)}")
        print(f"balance: {self.warehouse.balance}")
        print(f"foobars: {len(self.warehouse.foobars)}")
        print(f"foos: {len(self.warehouse.foos)}")
        print(f"bars: {len(self.warehouse.bars)}")
        print(f"finished: {self.stop_event.is_set()}")

    def print_state_monitoring(self) -> None:
        """
        Entrypoint of self.monitoring_thread, it prints the current state
        :return:
        """
        while not self.stop_event.is_set():
            self.print_state()
            time.sleep(settings.MONITORING_REFRESH_RATE * settings.TIME_RATIO)

