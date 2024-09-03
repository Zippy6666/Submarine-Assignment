from typing import NewType, Optional
import re, os, random


SerialNumber = NewType("SerialNumber", str)
Position = NewType("Position", list)


class SubmarineSystem:
    serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    def __init__(self) -> None:
        """The system for handling submarines"""
        self._submarines: dict[SerialNumber, self.Submarine] = {}
        self._make_dirs()

    def lookup_submarine(self, serial_number: SerialNumber) -> Optional["Submarine"]:
        """Get a submarine by serial number if it exists"""
        return self._submarines.get(serial_number)

    def register_submarine(self, serial_number: SerialNumber) -> None:
        """Register or overwrite a submarine of given serial_number"""
        if not self.serial_number_pattern.match(serial_number):
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")
        submarine: self.Submarine = self.Submarine(self, serial_number)
        self._submarines[serial_number] = submarine

    def simulate_movements(self, amount: int) -> None:
        for _, sub in self._submarines.items():
            for _ in range(amount):
                sub.move(random.choice(("up", "down", "left", "right")), random.randint(1, 10))


    def _make_dirs(self) -> None:
        """Make directories if not present."""
        os.makedirs("MovementReports", exist_ok=True)
        os.makedirs("Sensordata", exist_ok=True)
        os.makedirs("Secrets", exist_ok=True)

    def _log_submarine_movement(
        self, serial_number: SerialNumber, direction: str, distance: int
    ) -> None:
        with open("MovementReports/" + serial_number + ".txt", "a") as file:
            file.write(f"{direction} {distance}\n")

    def _log_submarine_sensors(self) -> None:
        raise NotImplementedError

    class Submarine:
        def __init__(
            self, system: "SubmarineSystem", serial_number: SerialNumber
        ) -> None:
            """A submarine."""
            self._serial_number: SerialNumber = serial_number
            self._position: Position = Position([0, 0])
            self._sensors: str = "1" * 208
            self._system: SubmarineSystem = system

        def move(self, direction: str, distance: int):
            match direction:
                case "up":
                    self._position[0] += distance
                case "down":
                    self._position[0] -= distance
                case "left":
                    self._position[1] -= distance
                case "right":
                    self._position[1] += distance
                case _:
                    raise ValueError("Not a valid direction.")
            self._system._log_submarine_movement(
                SerialNumber(self._serial_number), direction, distance
            )
        
        def __repr__( self ) -> str:
            return f"Submarine {self._serial_number} at {self._position}"


def main() -> None:
    system: SubmarineSystem = SubmarineSystem()

    # Register some example submarines
    for i in range(3000):
        serial_number: SerialNumber = SerialNumber(
            f"{i:04}2222-42"
        )
        system.register_submarine(serial_number)


    system.simulate_movements(300)



if __name__ == "__main__":
    main()
