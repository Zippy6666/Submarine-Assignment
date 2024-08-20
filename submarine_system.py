from typing import NewType
import re


SerialNumber = NewType('SerialNumber', str)


class Submarine:
    _serial_number_pattern = re.compile(r"^d{8}-d{2}$")

    def __init__(self, serial_number: SerialNumber) -> None:
        """ A submarine. """
        self.serial_number = serial_number

    @property
    def serial_number(self) -> str:
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value: str) -> None:
        if not self._serial_number_pattern.match(value):
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")
        self._serial_number = value


if __name__ == "__main__":
    sub = Submarine("00000000-00")