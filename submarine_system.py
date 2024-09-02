from typing import NewType
import re, os


SerialNumber = NewType('SerialNumber', str)
Position = NewType("Position", list)


class Submarine:
    _serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    def __init__(self, serial_number: SerialNumber) -> None:
        """ A submarine. """
        self._serial_number: SerialNumber = serial_number
        self._position: Position = [0, 0]
        self._sensors: str = "1"*208

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
    """ Make directories if not present """
    if not os.path.isdir("MovementReports"):
        os.mkdir("MovementReports")
    if not os.path.isdir("SensorData"):
        os.mkdir("SensorData")
    if not os.path.isdir("Secrets"):
        os.mkdir("Secrets")

def main() -> None:
    make_dirs()
    submarine = Submarine(SerialNumber("12345678-90"))
    print(submarine.serial_number)


if __name__ == "__main__":
    main()
    