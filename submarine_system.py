from collections.abc import Generator
from typing import NewType, Optional
from pathlib import Path
import re, os


SerialNumber = NewType("SerialNumber", str)
Position = NewType("Position", list[int])
SubmarineReport = NewType("SubmarineReport", str)


class SubmarineSystem:
    serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    def __init__(self) -> None:
        """The system for handling submarines."""

        self._submarines: dict[SerialNumber, self._Submarine] = {}

    def lookup_submarine(self, serial_number: SerialNumber) -> Optional[SubmarineReport]:
        """Get a submarine by serial number if it exists."""

        sub = self._submarines.get(serial_number)
        return str(sub)

    def register_submarine(self, serial_number: SerialNumber) -> None:
        """Register a submarine of given 'serial_number'."""

        if not self.serial_number_pattern.match(serial_number):
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")

        if not self._submarines.get(serial_number) is None:
            print(f"Warning: Submarine {serial_number} already registered! Overwriting.")

        # Create new submarine
        self._submarines[serial_number] = self._Submarine(serial_number)

    def register_submarines_by_movement_reports(self) -> Generator[SerialNumber]:
        """Register submarines by movement reports. Returns a generator that yields each serial number for the submarines."""

        if not os.path.isdir("MovementReports"):
            raise FileNotFoundError("No 'MovementReports' directory detected.")

        for file_name in os.listdir("MovementReports"):
            serial_number = Path(file_name).stem
            if self.serial_number_pattern.match(serial_number):
                self.register_submarine(serial_number)
                yield serial_number

    def move_submarine_by_reports(self, serial_number: SerialNumber) -> None:
        """Read movement reports for this submarine, and move it accordingly"""

        if not os.path.isfile(f"MovementReports/{serial_number}.txt"):
            raise FileNotFoundError("No movement reports file detected.")

        sub = self._submarines.get(serial_number)

        if sub is None:
            raise Exception(f"Submarine '{serial_number}' not found.")

        with open(f"MovementReports/{serial_number}.txt") as f:
            for i, line in enumerate(f):
                split = line.split()

                # This movement report was invalid, skip and continue
                if len(split) != 2 or not split[1].isdecimal():
                    print(f"Warning: Movement report {i+1} for {sub} is invalid. Skipping.")
                    continue

                sub.move(split[0], int(split[1]))

    def get_furthest_submarine(self) -> SubmarineReport:
        """Get the submarine furthest from the base."""

        sorted_subs = self._get_subs_sorted_dist()
        return str(sorted_subs[len(sorted_subs) - 1])

    def get_closest_submarine(self) -> SubmarineReport:
        """Get the submarine closest to the base."""

        sorted_subs = self._get_subs_sorted_dist()
        return str(sorted_subs[0])

    def get_lowest_submarine(self) -> SubmarineReport:
        """Get the submarine at the lowest point form the base."""

        sorted_subs = self._get_subs_sorted_vertical()
        return str(sorted_subs[0])

    def get_highest_submarine(self) -> SubmarineReport:
        """Get the submarine at the highest point from the base."""

        sorted_subs = self._get_subs_sorted_vertical()
        return str(sorted_subs[len(sorted_subs) - 1])

    def _get_subs_sorted_dist(self) -> list["_Submarine"]:
        """Get submarines sorted by distance from the base."""

        return sorted(self._submarines.values(), key=lambda submarine: submarine.dist_from_base)

    def _get_subs_sorted_vertical(self) -> list["_Submarine"]:
        """Get submarines sorted by altetude from the base."""

        return sorted(self._submarines.values(), key=lambda submarine: submarine.position[0])
    
    class _Submarine:
        def __init__(self, serial_number: SerialNumber) -> None:
            self._serial_number: SerialNumber = serial_number
            self._position: Position = Position([0, 0])

        @property
        def serial_number(self) -> SerialNumber:
            return self._serial_number

        @property
        def position(self) -> Position:
            return self._position

        @property
        def dist_from_base(self) -> float:
            """ The un-squared distance from the base. """
            return self._position[0] ** 2 + self._position[1] ** 2

        def move(self, dir: str, dist: int) -> None:
            match dir:
                case "up":
                    self._position[0] += dist
                case "down":
                    self._position[0] -= dist
                case "forward":
                    self._position[1] += dist
                case _:
                    print(f"Warning: Invalid direction '{dir}'")

        def __str__(self) -> str:
            return f"|Submarine {self._serial_number} at {self._position}>|"


def main() -> None:
    system: SubmarineSystem = SubmarineSystem()

    for serial_number in system.register_submarines_by_movement_reports():  # ~ 6 000 files
        system.move_submarine_by_reports(serial_number)  # ~ 100 000 line file read...

        report: SubmarineReport = system.lookup_submarine(serial_number)
        print(f"Movement reports fetched for {report}")


if __name__ == "__main__":
    main()
