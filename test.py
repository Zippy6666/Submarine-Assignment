from submarine_system import SubmarineSystem
from types import GeneratorType
import unittest


class SubSysTest(unittest.TestCase):
    def setUp(self) -> None:
        self.system = SubmarineSystem()

    def test_submarines_returns_generator(self):
        generator = self.system.submarines
        self.assertIsInstance(generator, GeneratorType)

    def test_max_move_logs_returns_int(self):
        self.assertIsInstance(self.system.max_move_logs, int)
    
    def test_collided_submarines_returns_valid_list(self):
        collided_subs = self.system.collided_submarines
        self.assertIsInstance(collided_subs, list)
        for sub in collided_subs:
            self.assertIsInstance(sub, str)

    def test_lookup_submarine_returns_none_or_submarineinfo(self):
        sub = self.system.lookup_submarine("123")
        self.assertIs(sub, None)

        self.system.register_submarine("78532608-69")
        sub = self.system.lookup_submarine("78532608-69")

        self.assertIsInstance(sub, str)

        self.system._submarines.clear()

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
    
    def test_count_sensor_errors_returns_valid_list(self):
        ...
    
    def test_count_sensor_errors_on_nonexistant_submarine(self):
        with self.assertRaises(LookupError):
            self.system.count_sensor_errors("123")
    
    def test_get_submarine_movement_log_returns_valid_deque(self):
        ...

    def test_get_sub_move_log_from_nonexistant_submarine(self):
        with self.assertRaises(LookupError):
            self.system.get_submarine_movement_log("123")
    
    def test_move_nonexistant_submarine_by_reports(self):
        with self.assertRaises(LookupError):
            self.system.move_submarine_by_reports("123")
    
    def test_get_submarines_by_position_when_none_registered(self):
        ...
    


if __name__ == "__main__":
    unittest.main()