from collections import deque
from collections.abc import Callable
from datetime import date
from submarine_system import SerialNumber, SubmarineSystem
import unittest


class SubSysTest(unittest.TestCase):
    def setUp(self) -> None:
        self.system = SubmarineSystem()

    @staticmethod
    def _create_test_submarine(serial_number: SerialNumber) -> Callable:
        """
        Decorator that creates one test submarine when conducting unit tests.
        All submarines are cleared after the test finished execution.
        """

        def decorator(func: Callable) -> Callable:
            def wrapper(sub_sys_test: "SubSysTest", *args, **kwargs):
                sub_sys_test.system.register_submarine(serial_number)

                return_value = func(sub_sys_test, *args, **kwargs)

                sub_sys_test.system.clear_submarines()

                return return_value

            return wrapper
        
        return decorator

    @_create_test_submarine("78532608-69")
    def test_count_sensor_errors_returns_valid_list(self):
        sensor_errors = self.system.count_sensor_errors("78532608-69")
        self.assertIsInstance(sensor_errors, list)

        for error_entry in sensor_errors:
            self.assertIsInstance(error_entry, dict)
            
    @_create_test_submarine("78532608-69")
    def test_get_submarine_movement_log_returns_valid_deque(self):
        self.system.move_submarine_by_reports("78532608-69")

        movement_log = self.system.get_submarine_movement_log("78532608-69")
        self.assertIsInstance(movement_log, deque)

        for entry in movement_log:
            self.assertIsInstance(entry, tuple)
            
    @_create_test_submarine("00000000-00")
    def test_activate_nuke_without_secret_key_or_launch_code(self):
        date_now_str = str( date.today() )
        secret_key = "Vvkn0pAqXmGEeNRAj2h03C3vI2x"
        activation_code = "RpojkncM1F1rr9xiiE"

        with self.assertRaises(LookupError):
            self.system.activate_nuke("00000000-00", date_now_str+secret_key+activation_code)

    def test_lookup_nonexistant_submarine(self):
        none = self.system.lookup_submarine("123")
        self.assertIsNone(none)

    def test_collided_submarines_returns_valid_list(self):
        collided_subs = self.system.collided_submarines
        self.assertIsInstance(collided_subs, list)
        for sub in collided_subs:
            self.assertIsInstance(sub, str)

    def test_register_faulty_submarine(self):
        with self.assertRaises(ValueError):
            self.system.register_submarine("hello")

    def test_order_faulty_torpedo(self):
        self.system.register_submarine("78532608-69")

        result = self.system.order_torpedo("78532608-69", "onwards")
        self.assertTrue(result is str or result is True)

        self.system._submarines.clear()

    def test_order_torpedo_from_nonexistant_submarine(self):
        with self.assertRaises(LookupError):
            self.system.order_torpedo("123", "up")
    
    def test_count_sensor_errors_on_nonexistant_submarine(self):
        with self.assertRaises(LookupError):
            self.system.count_sensor_errors("123")

    def test_get_sub_move_log_from_nonexistant_submarine(self):
        with self.assertRaises(LookupError):
            self.system.get_submarine_movement_log("123")
    
    def test_move_nonexistant_submarine_by_reports(self):
        with self.assertRaises(LookupError):
            self.system.move_submarine_by_reports("123")
    
    def test_get_submarines_by_position_when_none_registered(self):
        for method in (
            self.system.get_closest_submarine,
            self.system.get_furthest_submarine,
            self.system.get_lowest_submarine,
            self.system.get_highest_submarine,
        ):
            with self.assertRaises(ValueError):
                method()


if __name__ == "__main__":
    unittest.main()