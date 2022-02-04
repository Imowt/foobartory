from unittest.mock import Mock

from foobartory.core.factory import Factory
from foobartory.settings.settings import settings


class TestFactory:
    def setup_method(self):
        self.factory = Factory()

    def test_init_default_robots(self, mocker):
        """
        Test the init_default_robots method

        :param mocker: pytest mocker
        :return:
        """
        thread_start: Mock = mocker.patch("foobartory.core.factory.Thread.start")
        self.factory.init_default_robots()
        assert len(self.factory.warehouse.robots) == settings.DEFAULT_ROBOTS * 2
        assert thread_start.call_count == settings.DEFAULT_ROBOTS

    def test_run(self, mocker):
        """
        Test the run method

        :param mocker: pytest mocker
        :return:
        """
        print_state_mock: Mock = mocker.patch.object(Factory, "print_state")
        settings_mock: Mock = mocker.patch("foobartory.core.factory.settings")
        settings_mock.MAX_ROBOTS = len(self.factory.warehouse.robots)
        monitoring_thread_start_mock: Mock = Mock()
        self.factory.monitoring_thread.start = monitoring_thread_start_mock
        stop_event_set_mock: Mock = Mock()
        self.factory.stop_event.set = stop_event_set_mock
        self.factory.run()
        monitoring_thread_start_mock.assert_called_once()
        stop_event_set_mock.assert_called_once_with()
        print_state_mock.assert_called_once_with()

    def test_print_state(self, mocker):
        """
        Test the print_state method
        :param mocker: pytest mocker
        :return:
        """
        print_mock: Mock = mocker.patch("builtins.print")
        self.factory.print_state()

        assert print_mock.call_count == 7
        assert "robots:" in print_mock.call_args_list[1][0][0]
        assert "balance:" in print_mock.call_args_list[2][0][0]
        assert "foobars:" in print_mock.call_args_list[3][0][0]
        assert "foos:" in print_mock.call_args_list[4][0][0]
        assert "bars:" in print_mock.call_args_list[5][0][0]
        assert "finished:" in print_mock.call_args_list[6][0][0]

    def test_print_state_monitoring(self, mocker):
        """
        Test the print_state_monitoring method
        :param mocker: pytest mocker
        :return:
        """
        stop_event_is_set_mock: Mock = Mock()
        stop_event_is_set_mock.side_effect = [False, True]
        self.factory.stop_event.is_set = stop_event_is_set_mock

        print_state_mock: Mock = mocker.patch.object(Factory, "print_state")

        sleep_mock: Mock = mocker.patch('foobartory.core.factory.time.sleep')
        self.factory.print_state_monitoring()

        stop_event_is_set_mock.assert_called_with()
        print_state_mock.assert_called_once_with()
        sleep_mock.assert_called_once_with(settings.MONITORING_REFRESH_RATE * settings.TIME_RATIO)
