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

    class _SubmarineRegistry:
        def __init__(self) -> None:
            self._store: dict[SerialNumber, self.Submarine] = {}

        def retrieve(self, serial_number: SerialNumber) -> Optional["SubmarineSystem._Submarine"]:
            return self._store.get(serial_number)
        
        def _register(self, serial_number: SerialNumber, submarine: "SubmarineSystem._Submarine") -> None:
            self._store[serial_number] = submarine


    def __init__(self) -> None:
        """The system for handling submarines"""
        self._submarines: self._SubmarineRegistry = self._SubmarineRegistry()
        self._make_dirs()

    def _make_dirs(self) -> None:
        """Make directories if not present."""
        if not os.path.isdir("MovementReports"):
            os.mkdir("MovementReports")
        if not os.path.isdir("SensorData"):
            os.mkdir("SensorData")
        if not os.path.isdir("Secrets"):
            os.mkdir("Secrets")

    @property
    def submarines(self) -> _SubmarineRegistry:
        """The submarine registry in the system"""
        return self._submarines

    def register_submarine(self, serial_number: SerialNumber) -> None:
        """Register or overwrite a submarine of given serial_number"""
        if not self.serial_number_pattern.match(serial_number):
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")
        submarine: self._Submarine = self._Submarine(serial_number)
        self._submarines._register(SerialNumber(serial_number), submarine)


def main() -> None:
    system: SubmarineSystem = SubmarineSystem()

    # Register some example submarines
    for i in range(3000):
        serial_number = SerialNumber(f"{randint(1000, 9999)}{i:04}-{randint(10, 99)}")
        system.register_submarine(serial_number)

    print(system.submarines.retrieve("test"))
    print(system.submarines.retrieve(serial_number))


if __name__ == "__main__":
    main()
