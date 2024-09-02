from typing import NewType
from collections import defaultdict
from random import randint
import re, os


SerialNumber = NewType("SerialNumber", str)
Position = NewType("Position", list)


class SubmarineSystem:
    serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    class _Submarine:
        def __init__(self, serial_number: SerialNumber) -> None:
            """A submarine."""
            self.serial_number: SerialNumber = serial_number
            self.position: Position = [0, 0]
            self.sensors: str = "1" * 208

    def __init__(self) -> None:
        """A system for handling submarines"""
        self._submarines: defaultdict[SerialNumber, self.Submarine] = defaultdict(bool)
        self._make_dirs()

    def _make_dirs(self) -> None:
        """Make directories if not present."""
        if not os.path.isdir("MovementReports"):
            os.mkdir("MovementReports")
        if not os.path.isdir("SensorData"):
            os.mkdir("SensorData")
        if not os.path.isdir("Secrets"):
            os.mkdir("Secrets")

    def get_submarine(self, serial_number: SerialNumber) -> _Submarine | bool:
        """Return the submarine instance of the given serialnumber. Returns False if none was found."""
        return self._submarines[serial_number]

    def register_submarine(self, serial_number: SerialNumber) -> None:
        if not self.serial_number_pattern.match(serial_number):
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")
        submarine: self._Submarine = self._Submarine(serial_number)
        self._submarines[serial_number] = submarine


def main() -> None:
    submarine_system: SubmarineSystem = SubmarineSystem()

    # Register some example submarines
    for i in range(3000):
        submarine_system.register_submarine(f"{randint(1000, 9999)}{i:04}-{randint(10, 99)}")



if __name__ == "__main__":
    main()
