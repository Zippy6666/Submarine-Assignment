from collections.abc import Callable, Generator
from typing import NewType, Optional
from pathlib import Path
from collections import deque
import re, os


SerialNumber = NewType("SerialNumber", str)
Position = NewType("Position", list[int])
SubmarineInfo = NewType("SubmarineInfo", str)
MovementLogEntry = NewType("MovementLogEntry", tuple)
MovementLog = NewType("MovementLog", deque)
SensorError = NewType("SensorError", dict[str, int])
SensorErrorList = NewType("SensorErrorList", list)


class SubmarineSystem:
    serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    def __init__(self) -> None:
        """The system for handling submarines."""

        self._submarines: dict[SerialNumber, self._Submarine] = {}

    def _get_sub(self, serial_number: SerialNumber) -> "SubmarineSystem._Submarine":
        return self._submarines.get(serial_number)

    def lookup_submarine(self, serial_number: SerialNumber) -> Optional[SubmarineInfo]:
        """Get a submarine by serial number if it exists."""

        return str( self._get_sub(serial_number) )

    def register_submarine(self, serial_number: SerialNumber) -> None:
        """Register a submarine of given 'serial_number'."""

        if not self.serial_number_pattern.match(serial_number):
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")

        if not self._get_sub(serial_number) is None:
            print(f"Warning: Submarine {serial_number} already registered! Overwriting.")

        # Create new submarine
        self._submarines[serial_number] = self._Submarine(serial_number)

    def count_sensor_errors(self, serial_number: SerialNumber) -> SensorErrorList:
        """Returns a list of all types of sensor errors that occured, how many times they occured, and how many sensors that failed during said error/errors."""

        if not os.path.isdir("Sensordata"):
            raise FileNotFoundError("No 'Sensordata' directory detected.")
        
        sub = self._get_sub(serial_number)
        if sub is None:
            raise Exception(f"Submarine '{serial_number}' not found.")

        errors: dict[str, SensorError] = {}
        for line in sub.sensor_data:
            if not "0" in line: continue # No error

            if not errors.get(line):
                sensor_failures = line.count("0") # use str.count, since it is implemented in C, it is faster than looping through the string
                error: SensorError = dict(sensor_failures=sensor_failures, error_occurences=1)
                errors[line] = error # New error type, register 1
            else:
                errors[line]["error_occurences"] += 1 # Reoccuring error, add 1

        return list( errors.values() )

    def get_submarine_movement_log(self, serial_number: SerialNumber) -> MovementLog:
        """Retrieve the latest movement logs for the submarine."""

        sub = self._get_sub(serial_number)
        return sub.movement_log
    
    def get_submarine_count_by_movement_reports(self) -> int:
        """Gets how many submarines are listed in the movement reports."""

        if not os.path.isdir("MovementReports"):
            raise FileNotFoundError("No 'MovementReports' directory detected.")
        
        list_dir = os.listdir("MovementReports")
        return len(list_dir)
        
    def register_submarines_by_movement_reports(self) -> Generator[SerialNumber, int]:
        """Register submarines by movement reports. Returns a generator that yields each serial number for the submarines."""

        if not os.path.isdir("MovementReports"):
            raise FileNotFoundError("No 'MovementReports' directory detected.")

        list_dir = os.listdir("MovementReports")
        for i, file_name in enumerate( list_dir, start=1 ):
            serial_number = Path(file_name).stem
            self.register_submarine(serial_number)
            yield serial_number, i

    # TODO: Practice speed over memory here since files are not as large as sensordata files
    def move_submarine_by_reports(self, serial_number: SerialNumber) -> None:
        """Read movement reports for this submarine, and move it accordingly"""

        sub = self._get_sub(serial_number)

        if sub is None:
            raise Exception(f"Submarine '{serial_number}' not found.")

        for dir, dist in sub.movement:
            sub.move(dir, dist)

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
            self._movement_log: MovementLog = deque(maxlen=self._max_logs)

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

        @property
        def sensor_data(self) -> Generator[str]:
            if not os.path.isfile(f"Sensordata/{self.serial_number}.txt"):
                raise FileNotFoundError("No sensor data file detected.")
        
            with open(f"Sensordata/{self.serial_number}.txt") as f:
                for line in f:
                    yield line

        @property
        def movement(self) -> Generator[str, int]:
            if not os.path.isfile(f"MovementReports/{self.serial_number}.txt"):
                raise FileNotFoundError("No movement reports file detected.")

            with open(f"MovementReports/{self.serial_number}.txt") as f:
                for line in f:
                    split = line.split()

                    # This movement report was invalid, skip and continue
                    if len(split) != 2 or not split[1].isdigit():
                        print(f"Warning: One movement report for {self} is invalid. Skipping.")
                        continue

                    yield split[0], int(split[1])

        @staticmethod
        def _log_movement(func: Callable) -> Callable:
            def wrapper(self, dir, dist):
                old_pos = [self.position[0], self.position[1]]
                
                return_value = func(self, dir, dist)

                new_pos = [self.position[0], self.position[1]]
                
                log_entry: MovementLogEntry = (old_pos, dir, dist, new_pos)
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
    submarine_max = system.get_submarine_count_by_movement_reports()


    # Register and move all submarines by their reports
    print("Registering and moving subs by reports...")
    for serial_number, current_count in system.register_submarines_by_movement_reports():
        system.move_submarine_by_reports(serial_number)
        sensor_errors: SensorErrorList = system.count_sensor_errors(serial_number)
        print(f"{current_count}/{submarine_max} movement reports and sensor errors fetched!")
    print("------------------------------------------------------")


    # Get an example submarine to showcase features on
    example_sub: SubmarineInfo = system.lookup_submarine(serial_number)
    

    # Show example submarine sensor errors
    print(f"Example {example_sub} sensor errors:")
    for i, error in enumerate(sensor_errors, start=1):
        print(f"Error type {i}: {error}")
    print("------------------------------------------------------")


    # Show example submarine
    print(f"Example {example_sub} movement log:")
    movement_log: MovementLog = system.get_submarine_movement_log(serial_number)
    for entry in movement_log:
        print(entry)
    print("------------------------------------------------------")


    # Show location information
    print("Submarine location information:")
    closest: SubmarineInfo = system.get_closest_submarine()
    furthest: SubmarineInfo = system.get_furthest_submarine()
    highest: SubmarineInfo = system.get_highest_submarine()
    lowest: SubmarineInfo = system.get_lowest_submarine()
    print(f"Closest: {closest}, furthest: {furthest}, highest: {highest}, lowest: {lowest}")
    print("------------------------------------------------------")


if __name__ == "__main__":
    main()
