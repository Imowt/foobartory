from unittest.mock import Mock

from foobartory.core.models.items.bar import Bar
from foobartory.core.models.items.foo import Foo
from foobartory.core.models.items.foobar import FooBar
from foobartory.core.models.robot.enums.robot_action import RobotActivity
from foobartory.core.models.warehouse import Warehouse
from foobartory.core.robot import Robot
from foobartory.settings.settings import settings


class TestRobot:
    def setup_method(self):
        self.stop_event_mock: Mock = Mock()
        self.robot: Robot = Robot(robot_id=1, warehouse=Warehouse(), stop_event=self.stop_event_mock)

    def test_run(self, mocker):
        """
        Test the run method
        :param mocker: pytest mocker
        :return:
        """
        stop_event_is_set_mock: Mock = Mock()
        stop_event_is_set_mock.side_effect = [False, True]
        self.robot.stop_event.is_set = stop_event_is_set_mock

        execute_next_activity_mock: Mock = mocker.patch.object(Robot, "execute_next_activity")

        self.robot.run()

        assert stop_event_is_set_mock.call_count == 2
        execute_next_activity_mock.assert_called_once_with()

    def test_execute_next_activity(self, mocker):
        """
        Test the execute_next_action method, with different next activity,
        so it should move, then ask again the next activity to check if it's still valid
        then execute it
        :param mocker: pytest mocker
        :return:
        """
        self.robot.activity = RobotActivity.MINING_FOO
        next_activity: RobotActivity = RobotActivity.ASSEMBLING_FOOBAR
        get_next_activity_mock: Mock = mocker.patch.object(Robot, "get_next_activity")
        get_next_activity_mock.side_effect = [next_activity, next_activity]

        move_mock: Mock = mocker.patch.object(Robot, "move")

        execute_activity_mock: Mock = mocker.patch.object(Robot, "execute_activity")

        stop_event_is_set_mock: Mock = Mock()
        stop_event_is_set_mock.return_value = False
        self.robot.stop_event.is_set = stop_event_is_set_mock

        self.robot.execute_next_activity()

        move_mock.assert_called_once_with()
        stop_event_is_set_mock.assert_called_once_with()
        assert get_next_activity_mock.call_count == 2
        assert self.robot.activity == next_activity
        execute_activity_mock.assert_called_once_with()

    def test_execute_same_activity(self, mocker):
        """
        Test the execute_next_action method, with the same activity
        :param mocker: pytest mocker
        :return:
        """
        next_activity: RobotActivity = RobotActivity.ASSEMBLING_FOOBAR
        self.robot.activity = next_activity
        get_next_activity_mock: Mock = mocker.patch.object(Robot, "get_next_activity")
        get_next_activity_mock.side_effect = [next_activity, next_activity]

        move_mock: Mock = mocker.patch.object(Robot, "move")

        execute_activity_mock: Mock = mocker.patch.object(Robot, "execute_activity")

        stop_event_is_set_mock: Mock = Mock()
        stop_event_is_set_mock.return_value = False
        self.robot.stop_event.is_set = stop_event_is_set_mock

        self.robot.execute_next_activity()

        move_mock.assert_not_called()
        stop_event_is_set_mock.assert_called_once_with()
        assert get_next_activity_mock.call_count == 2
        assert self.robot.activity == next_activity
        execute_activity_mock.assert_called_once_with()

    def test_execute_activity_changed_after_move_call(self, mocker):
        """
        Test the execute_next_action method, the activity changed during the move duration
        :param mocker: pytest mocker
        :return:
        """
        robot_final_activity = RobotActivity.BUYING_ROBOT
        get_next_activity_mock: Mock = mocker.patch.object(Robot, "get_next_activity")
        get_next_activity_mock.side_effect = [RobotActivity.ASSEMBLING_FOOBAR, robot_final_activity,
                                              robot_final_activity, robot_final_activity]

        move_mock: Mock = mocker.patch.object(Robot, "move")

        execute_activity_mock: Mock = mocker.patch.object(Robot, "execute_activity")

        stop_event_is_set_mock: Mock = Mock()
        stop_event_is_set_mock.return_value = False
        self.robot.stop_event.is_set = stop_event_is_set_mock

        self.robot.execute_next_activity()

        assert move_mock.call_count == 2
        assert stop_event_is_set_mock.call_count == 2
        assert get_next_activity_mock.call_count == 4
        assert self.robot.activity == robot_final_activity
        execute_activity_mock.assert_called_once_with()

    def test_get_next_activity_buy_robot(self, mocker):
        """
        Test the get_next_activity method, can buy robot
        :param mocker: pytest mocker
        :return:
        """
        can_buy_robot_mock: Mock = mocker.patch.object(Robot, "can_buy_robot")
        can_buy_robot_mock.return_value = True

        next_activity: RobotActivity = self.robot.get_next_activity()

        assert next_activity == RobotActivity.BUYING_ROBOT

    def test_get_next_activity_enough_balance_to_buy_robot(self, mocker):
        """
        Test the get_next_activity method, with enough balance to buy robot but not enough foo
        :param mocker: pytest mocker
        :return:
        """
        can_buy_robot_mock: Mock = mocker.patch.object(Robot, "can_buy_robot")
        can_buy_robot_mock.return_value = False
        has_enough_balance_to_buy_robot_mock: Mock = mocker.patch.object(Robot, "has_enough_balance_to_buy_robot")
        has_enough_balance_to_buy_robot_mock.return_value = True

        next_activity: RobotActivity = self.robot.get_next_activity()

        assert next_activity == RobotActivity.MINING_FOO

    def test_get_next_activity_can_sell_foobars(self, mocker):
        """
        Test the get_next_activity method, with can_sell_foobars True
        :param mocker: pytest mocker
        :return:
        """
        can_buy_robot_mock: Mock = mocker.patch.object(Robot, "can_buy_robot")
        can_buy_robot_mock.return_value = False
        has_enough_balance_to_buy_robot_mock: Mock = mocker.patch.object(Robot, "has_enough_balance_to_buy_robot")
        has_enough_balance_to_buy_robot_mock.return_value = False
        can_sell_foobars_mock: Mock = mocker.patch.object(Robot, "can_sell_foobars")
        can_sell_foobars_mock.return_value = True

        next_activity: RobotActivity = self.robot.get_next_activity()

        assert next_activity == RobotActivity.SELLING_FOOBARS

    def test_get_next_activity_can_assemble_foobar(self, mocker):
        """
        Test the get_next_activity method, with can_assemble_foobar True
        :param mocker: pytest mocker
        :return:
        """
        can_buy_robot_mock: Mock = mocker.patch.object(Robot, "can_buy_robot")
        can_buy_robot_mock.return_value = False
        has_enough_balance_to_buy_robot_mock: Mock = mocker.patch.object(Robot, "has_enough_balance_to_buy_robot")
        has_enough_balance_to_buy_robot_mock.return_value = False
        can_sell_foobars_mock: Mock = mocker.patch.object(Robot, "can_sell_foobars")
        can_sell_foobars_mock.return_value = False
        can_assemble_foobar_mock: Mock = mocker.patch.object(Robot, "can_assemble_foobar")
        can_assemble_foobar_mock.return_value = True

        next_activity: RobotActivity = self.robot.get_next_activity()

        assert next_activity == RobotActivity.ASSEMBLING_FOOBAR

    def test_get_next_activity_not_enough_foo_to_buy_robot(self, mocker):
        """
        Test the get_next_activity method, with has_enough_foo_to_buy_robot False
        :param mocker: pytest mocker
        :return:
        """
        can_buy_robot_mock: Mock = mocker.patch.object(Robot, "can_buy_robot")
        can_buy_robot_mock.return_value = False
        has_enough_balance_to_buy_robot_mock: Mock = mocker.patch.object(Robot, "has_enough_balance_to_buy_robot")
        has_enough_balance_to_buy_robot_mock.return_value = False
        can_sell_foobars_mock: Mock = mocker.patch.object(Robot, "can_sell_foobars")
        can_sell_foobars_mock.return_value = False
        can_assemble_foobar_mock: Mock = mocker.patch.object(Robot, "can_assemble_foobar")
        can_assemble_foobar_mock.return_value = False
        has_enough_foo_to_buy_robot_mock: Mock = mocker.patch.object(Robot, "has_enough_foo_to_buy_robot")
        has_enough_foo_to_buy_robot_mock.return_value = False

        next_activity: RobotActivity = self.robot.get_next_activity()

        assert next_activity == RobotActivity.MINING_FOO

    def test_get_next_activity_mining_bar(self, mocker):
        """
        Test the get_next_activity method else
        :param mocker: pytest mocker
        :return:
        """
        can_buy_robot_mock: Mock = mocker.patch.object(Robot, "can_buy_robot")
        can_buy_robot_mock.return_value = False
        has_enough_balance_to_buy_robot_mock: Mock = mocker.patch.object(Robot, "has_enough_balance_to_buy_robot")
        has_enough_balance_to_buy_robot_mock.return_value = False
        can_sell_foobars_mock: Mock = mocker.patch.object(Robot, "can_sell_foobars")
        can_sell_foobars_mock.return_value = False
        can_assemble_foobar_mock: Mock = mocker.patch.object(Robot, "can_assemble_foobar")
        can_assemble_foobar_mock.return_value = False
        has_enough_foo_to_buy_robot_mock: Mock = mocker.patch.object(Robot, "has_enough_foo_to_buy_robot")
        has_enough_foo_to_buy_robot_mock.return_value = True

        next_activity: RobotActivity = self.robot.get_next_activity()

        assert next_activity == RobotActivity.MINING_BAR

    def test_execute_activity_buy_robot(self, mocker):
        """
        Test the execute_activity method, buy robot call
        :param mocker: pytest mocker
        :return:
        """
        self.robot.activity = RobotActivity.BUYING_ROBOT
        buy_robot_mock: Mock = mocker.patch.object(Robot, 'buy_robot')
        self.robot.execute_activity()
        buy_robot_mock.assert_called_once_with()

    def test_execute_activity_mine_foo(self, mocker):
        """
        Test the execute_activity method, mine_foo call
        :param mocker: pytest mocker
        :return:
        """
        self.robot.activity = RobotActivity.MINING_FOO
        mine_foo_mock: Mock = mocker.patch.object(Robot, 'mine_foo')
        self.robot.execute_activity()
        mine_foo_mock.assert_called_once_with()

    def test_execute_activity_mine_bar(self, mocker):
        """
        Test the execute_activity method, mine_bar call
        :param mocker: pytest mocker
        :return:
        """
        self.robot.activity = RobotActivity.MINING_BAR
        mine_bar_mock: Mock = mocker.patch.object(Robot, 'mine_bar')
        self.robot.execute_activity()
        mine_bar_mock.assert_called_once_with()

    def test_execute_activity_selling_foobars(self, mocker):
        """
        Test the execute_activity method, selling_foobars call
        :param mocker: pytest mocker
        :return:
        """
        self.robot.activity = RobotActivity.SELLING_FOOBARS
        selling_foobars_mock: Mock = mocker.patch.object(Robot, 'sell_foobars')
        self.robot.execute_activity()
        selling_foobars_mock.assert_called_once_with()

    def test_execute_activity_assemble_foobar(self, mocker):
        """
        Test the execute_activity method, assemble_foobar call
        :param mocker: pytest mocker
        :return:
        """
        self.robot.activity = RobotActivity.ASSEMBLING_FOOBAR
        assemble_foobar_mock: Mock = mocker.patch.object(Robot, 'assemble_foobar')
        self.robot.execute_activity()
        assemble_foobar_mock.assert_called_once_with()

    def test_wait(self, mocker):
        """
        Test the wait method
        :param mocker: pytest mocker
        :return:
        """
        sleep_mock: Mock = mocker.patch('foobartory.core.robot.time.sleep')
        second: int = 1
        self.robot.wait(second)
        sleep_mock.assert_called_once_with(second * settings.TIME_RATIO)

    def test_move(self, mocker):
        """
        Test the move method
        :param mocker: pytest mocker
        :return:
        """
        wait_mock: Mock = mocker.patch.object(Robot, 'wait')
        self.robot.move()
        wait_mock.assert_called_once_with(settings.ROBOT_MOVING_DURATION)

    def test_mine_foo(self, mocker):
        """
        Test the mine_foo method
        :param mocker: pytest mocker
        :return:
        """
        base_foos_length = len(self.robot.warehouse.foos)
        wait_mock: Mock = mocker.patch.object(Robot, 'wait')
        self.robot.mine_foo()
        wait_mock.assert_called_once_with(settings.ROBOT_MINING_FOO_DURATION)

        assert len(self.robot.warehouse.foos) == base_foos_length + 1

    def test_mine_bar(self, mocker):
        """
        Test the mine_bar method
        :param mocker: pytest mocker
        :return:
        """
        base_bars_length = len(self.robot.warehouse.bars)
        wait_mock: Mock = mocker.patch.object(Robot, 'wait')
        self.robot.mine_bar()
        wait_mock.assert_called_once()

        wait_argument = wait_mock.call_args_list[0][0][0]
        assert len(self.robot.warehouse.bars) == base_bars_length + 1
        assert wait_argument >= settings.ROBOT_MINING_BAR_DURATION_MIN
        assert wait_argument <= settings.ROBOT_MINING_BAR_DURATION_MAX

    def test_can_assemble_foobar(self, ):
        """
        Test the can_assemble_foobar method
        :return:
        """
        assert self.robot.can_assemble_foobar() == (
                    len(self.robot.warehouse.foos) > 0 and len(self.robot.warehouse.bars) > 0)

    def test_assemble_foobar_success(self, mocker):
        """
        Test the assemble_foobar method success
        :param mocker: pytest mocker
        :return:
        """
        foo: Foo = Foo()
        bar: Bar = Bar()
        self.robot.warehouse.foos.append(foo)
        self.robot.warehouse.bars.append(bar)

        wait_mock: Mock = mocker.patch.object(Robot, 'wait')
        randrange_mock: Mock = mocker.patch('foobartory.core.robot.random.randrange')
        randrange_mock.return_value = settings.ROBOT_ASSEMBLING_FOOBAR_SUCCESS_RATE - 1
        self.robot.assemble_foobar()

        wait_mock.assert_called_once_with(settings.ROBOT_ASSEMBLING_FOOBAR_DURATION)
        assert len(self.robot.warehouse.foobars) == 1
        assert self.robot.warehouse.foobars[0].bar == bar
        assert self.robot.warehouse.foobars[0].foo == foo

    def test_assemble_foobar_fail(self, mocker):
        """
        Test the assemble_foobar method
        :param mocker: pytest mocker
        :return:
        """
        foo: Foo = Foo()
        bar: Bar = Bar()
        self.robot.warehouse.foos.append(foo)
        self.robot.warehouse.bars.append(bar)

        wait_mock: Mock = mocker.patch.object(Robot, 'wait')
        randrange_mock: Mock = mocker.patch('foobartory.core.robot.random.randrange')
        randrange_mock.return_value = settings.ROBOT_ASSEMBLING_FOOBAR_SUCCESS_RATE + 1
        self.robot.assemble_foobar()

        wait_mock.assert_called_once_with(settings.ROBOT_ASSEMBLING_FOOBAR_DURATION)
        assert len(self.robot.warehouse.foobars) == 0
        assert self.robot.warehouse.bars[0] == bar
        assert len(self.robot.warehouse.foos) == 0

    def test_can_sell_foobars(self):
        """
        Test the can_sell_foobars method
        :return:
        """
        assert self.robot.can_sell_foobars() == (len(self.robot.warehouse.foobars) > settings.ROBOT_SELLING_FOOBARS_MIN)

    def test_get_foobars_to_sell_one_foobar(self):
        """
        Test the get_foobars_to_sell method with one foobar
        :return:
        """
        self.robot.warehouse.foobars.append(FooBar(foo=Foo(), bar=Bar()))
        assert len(self.robot.get_foobars_to_sell()) == 1

    def test_get_foobars_to_sell_multiple_foobars(self):
        """
        Test the get_foobars_to_sell method with 6 foobars
        :return:
        """
        for _ in range(6):
            self.robot.warehouse.foobars.append(FooBar(foo=Foo(), bar=Bar()))

        assert len(self.robot.get_foobars_to_sell()) == settings.ROBOT_SELLING_FOOBARS_MAX

    def test_selling_foobars(self, mocker):
        """
        Test the selling_foobars method
        :param mocker: pytest mocker
        :return:
        """
        get_foobars_to_sell_mock: Mock = mocker.patch.object(Robot, 'get_foobars_to_sell')
        get_foobars_to_sell_mock_return = [FooBar(foo=Foo(), bar=Bar()), FooBar(foo=Foo(), bar=Bar())]
        get_foobars_to_sell_mock.return_value = get_foobars_to_sell_mock_return

        wait_mock: Mock = mocker.patch.object(Robot, 'wait')

        self.robot.sell_foobars()

        get_foobars_to_sell_mock.assert_called_once_with()
        wait_mock.assert_called_once_with(settings.ROBOT_SELLING_FOOBARS_DURATION)
        assert self.robot.warehouse.balance == (settings.FOOBAR_VALUE * len(get_foobars_to_sell_mock_return))

    def test_can_buy_robot_true(self, mocker):
        """
        test the can_buy_robot method,
        :param mocker: pytest mocker
        :return:
        """
        has_enough_balance_to_buy_robot_mock = mocker.patch.object(Robot,  'has_enough_balance_to_buy_robot')
        has_enough_balance_to_buy_robot_mock.return_value = True
        has_enough_foo_to_buy_robot_mock = mocker.patch.object(Robot,  'has_enough_foo_to_buy_robot')
        has_enough_foo_to_buy_robot_mock.return_value = True

        assert self.robot.can_buy_robot()

    def test_can_buy_robot_not_enough_foos(self, mocker):
        """
        test the can_buy_robot method, not enough foos
        :param mocker: pytest mocker
        :return:
        """
        has_enough_balance_to_buy_robot_mock = mocker.patch.object(Robot,  'has_enough_balance_to_buy_robot')
        has_enough_balance_to_buy_robot_mock.return_value = True
        has_enough_foo_to_buy_robot_mock = mocker.patch.object(Robot,  'has_enough_foo_to_buy_robot')
        has_enough_foo_to_buy_robot_mock.return_value = False

        assert not self.robot.can_buy_robot()

    def test_can_buy_robot_not_enough_balance(self, mocker):
        """
        test the can_buy_robot method, not enough balance
        :param mocker: pytest mocker
        :return:
        """
        has_enough_balance_to_buy_robot_mock = mocker.patch.object(Robot, 'has_enough_balance_to_buy_robot')
        has_enough_balance_to_buy_robot_mock.return_value = False
        has_enough_foo_to_buy_robot_mock = mocker.patch.object(Robot, 'has_enough_foo_to_buy_robot')
        has_enough_foo_to_buy_robot_mock.return_value = True

        assert not self.robot.can_buy_robot()

    def test_has_enough_balance_to_buy_robot(self):
        """
        test the has_enough_balance_to_buy_robot True
        :return:
        """
        self.robot.warehouse.balance = settings.ROBOT_COST
        assert self.robot.has_enough_balance_to_buy_robot()

    def test_has_enough_balance_to_buy_robot_false(self):
        """
        test the has_enough_balance_to_buy_robot False
        :return:
        """
        self.robot.warehouse.balance = 0
        assert not self.robot.has_enough_balance_to_buy_robot()

    def test_has_enough_foo_to_buy_robot(self):
        """
        test the has_enough_foo_to_buy_robot True
        :return:
        """
        for _ in range(settings.ROBOT_FOO_COST):
            self.robot.warehouse.foos.append(Foo())
        assert self.robot.has_enough_foo_to_buy_robot()

    def test_has_enough_foo_to_buy_robot_false(self):
        """
        test the has_enough_foo_to_buy_robot false
        :return:
        """
        self.robot.warehouse.foos = []
        assert not self.robot.has_enough_foo_to_buy_robot()

    def test_buy_robot(self, mocker):
        """
        Test the buy_robot method

        :param mocker: pytest mocker
        :return:
        """
        self.robot.warehouse.balance = settings.ROBOT_COST
        base_robots_length = len(self.robot.warehouse.robots)
        for _ in range(settings.ROBOT_FOO_COST):
            self.robot.warehouse.foos.append(Foo())

        start_mock: Mock = mocker.patch.object(Robot, 'start')

        self.robot.buy_robot()

        assert self.robot.warehouse.balance == 0
        assert len(self.robot.warehouse.robots) == base_robots_length + 1
        start_mock.assert_called_once_with()



