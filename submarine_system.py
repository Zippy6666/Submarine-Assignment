from collections.abc import Callable, Generator
from typing import NewType, Optional
from pathlib import Path
import re, os, atexit


SerialNumber = NewType("SerialNumber", str)
Position = NewType("Position", list[int])
SubmarineInfo = NewType("SubmarineInfo", str)
MovementLogEntry = NewType("MovementLogEntry", str)
MovementLog = NewType("MovementLog", list[MovementLogEntry])


class SubmarineSystem:
    serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    def __init__(self) -> None:
        """The system for handling submarines."""

        self._submarines: dict[SerialNumber, self._Submarine] = {}

    def lookup_submarine(self, serial_number: SerialNumber) -> Optional[SubmarineInfo]:
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

    def count_sensor_errors(self, serial_number: SerialNumber):
        """Not implemented."""

        if not os.path.isdir("Sensordata"):
            raise FileNotFoundError("No 'Sensordata' directory detected.")
        
        raise NotImplementedError()

    def get_submarine_movement_log(self, serial_number: SerialNumber) -> MovementLog:
        """Retrieve the latest movement logs for the submarine."""
        sub = self._submarines.get(serial_number)
        return sub.movement_log
    
    def register_submarines_by_movement_reports(self) -> Generator[SerialNumber]:
        """Register submarines by movement reports. Returns a generator that yields each serial number for the submarines."""

        if not os.path.isdir("MovementReports"):
            raise FileNotFoundError("No 'MovementReports' directory detected.")

        for file_name in os.listdir("MovementReports"):
            serial_number = Path(file_name).stem
            self.register_submarine(serial_number)
            yield serial_number

    def move_submarine_by_reports(self, serial_number: SerialNumber) -> SubmarineInfo:
        """Read movement reports for this submarine, and move it accordingly"""

        if not os.path.isfile(f"MovementReports/{serial_number}.txt"):
            raise FileNotFoundError("No movement reports file detected.")

        sub = self._submarines.get(serial_number)

        if sub is None:
            raise Exception(f"Submarine '{serial_number}' not found.")

        with open(f"MovementReports/{serial_number}.txt") as f:
            for line in f:
                split = line.split()

                # This movement report was invalid, skip and continue
                if len(split) != 2 or not split[1].isdecimal():
                    print(f"Warning: One movement report for {sub} is invalid. Skipping.")
                    continue

                sub.move(split[0], int(split[1]))
        
        return str(sub)

    def get_furthest_submarine(self) -> SubmarineInfo:
        """Get the submarine furthest from the base."""

        sorted_subs = self._get_subs_sorted_dist()
        return str(sorted_subs[len(sorted_subs) - 1])

    def get_closest_submarine(self) -> SubmarineInfo:
        """Get the submarine closest to the base."""

        sorted_subs = self._get_subs_sorted_dist()
        return str(sorted_subs[0])

    def get_lowest_submarine(self) -> SubmarineInfo:
        """Get the submarine at the lowest point form the base."""

        sorted_subs = self._get_subs_sorted_vertical()
        return str(sorted_subs[0])

    def get_highest_submarine(self) -> SubmarineInfo:
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
        _max_logs = 100

        def __init__(self, serial_number: SerialNumber) -> None:
            self._serial_number: SerialNumber = serial_number
            self._position: Position = Position([0, 0])
            self._movement_log: MovementLog = []

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

        @property
        def movement_log(self) -> MovementLog:
            return self._movement_log

        @staticmethod
        def _log_movement(func: Callable) -> Callable:
            def wrapper(self, dir, dist):
                old_pos = self.position.copy()
                
                return_value = func(self, dir, dist)
                
                log_entry: MovementLogEntry = f"{old_pos} {dir} {dist} {self.position}"

                # Limit the log size
                if len(self._movement_log) >= self._max_logs:
                    self._movement_log.pop(0)

                self._movement_log.append(log_entry)

                return return_value

            return wrapper

        @_log_movement
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
            return f"|Submarine {self._serial_number} at {self._position}|"


def main() -> None:
    system: SubmarineSystem = SubmarineSystem()

    def at_exit():
        closest: SubmarineInfo = system.get_closest_submarine()
        furthest: SubmarineInfo = system.get_furthest_submarine()
        highest: SubmarineInfo = system.get_highest_submarine()
        lowest: SubmarineInfo = system.get_lowest_submarine()
        print("SUBMARINE LOCATION INFO:")
        print(f"Closest: {closest}, furthest: {furthest}, highest: {highest}, lowest: {lowest}")

    atexit.register(at_exit)
    
    # system.register_submarine("10053472-25")
    # system.move_submarine_by_reports("10053472-25")
    # movement_log = system.get_submarine_movement_log("10053472-25")
    # for i, entry in enumerate(movement_log, start=1):
    #     print(f"Entry {i} = {entry}")

    for serial_number in system.register_submarines_by_movement_reports():  # ~ 6 000 files
        info: SubmarineInfo = system.move_submarine_by_reports(serial_number)  # ~ 100 000 line file read...
        print(f"Movement reports fetched for {info}")


if __name__ == "__main__":
    main()
