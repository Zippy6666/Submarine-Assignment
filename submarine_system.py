from typing import NewType
import re, os


SerialNumber = NewType('SerialNumber', str)


class Submarine:
    _serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    def __init__(self, serial_number: SerialNumber) -> None:
        """ A submarine. """
        self.serial_number = serial_number

    @property
    def serial_number(self) -> str:
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value: str) -> None:
        if self._serial_number_pattern.match(value):
            self._serial_number = value
        else:
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")


def make_dirs() -> None:
    """ Make directories"""
    if not os.path.isdir("MovementReports"):
        os.mkdir("MovementReports")
    if not os.path.isdir("SensorData"):
        os.mkdir("SensorData")


def main() -> None:
    make_dirs()


if __name__ == "__main__":
    main()
    