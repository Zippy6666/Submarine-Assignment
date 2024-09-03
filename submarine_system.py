from typing import NewType, Optional
from random import randint
import re, os


SerialNumber = NewType("SerialNumber", str)
Position = NewType("Position", list)


class SubmarineSystem:
    serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    class _Submarine:
        def __init__(self, serial_number: SerialNumber) -> None:
            """A submarine."""
            self._serial_number: SerialNumber = serial_number
            self._position: Position = Position([0, 0])
            self._sensors: str = "1" * 208

    def __init__(self) -> None:
        """The system for handling submarines"""
        self._submarines: dict[SerialNumber, self._Submarine] = {}
        self._make_dirs()

    def _make_dirs(self) -> None:
        """Make directories if not present."""
        if not os.path.isdir("MovementReports"):
            os.mkdir("MovementReports")
        if not os.path.isdir("SensorData"):
            os.mkdir("SensorData")
        if not os.path.isdir("Secrets"):
            os.mkdir("Secrets")

    def lookup_submarine(self, serial_number:SerialNumber) -> Optional[_Submarine]:
        """Get a submarine by serial number if it exists"""
        return self._submarines.get(serial_number)

    def register_submarine(self, serial_number: SerialNumber) -> None:
        """Register or overwrite a submarine of given serial_number"""
        if not self.serial_number_pattern.match(serial_number):
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")
        submarine: self._Submarine = self._Submarine(serial_number)
        self._submarines[serial_number] = submarine


def main() -> None:
    system: SubmarineSystem = SubmarineSystem()

    # Register some example submarines
    for i in range(3000):
        serial_number: SerialNumber = SerialNumber(f"{randint(1000, 9999)}{i:04}-{randint(10, 99)}")
        system.register_submarine(serial_number)

    print(system.lookup_submarine("hello"))
    print(system.lookup_submarine(serial_number))


if __name__ == "__main__":
    main()
