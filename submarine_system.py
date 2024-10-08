"""Run this!"""


from collections.abc import Callable, Generator
from enum import Enum
from typing import NewType, Optional, Union
from pathlib import Path
from collections import deque
from datetime import date
import re, os, sys, random, time, hashlib


SerialNumber = NewType("SerialNumber", str)
Position = NewType("Position", list[int])
SubmarineInfo = NewType("SubmarineInfo", str)
MovementLogEntry = NewType("MovementLogEntry", tuple)
MovementLog = NewType("MovementLog", deque)
SensorError = NewType("SensorError", dict[str, int])
SensorErrorList = NewType("SensorErrorList", list)
Direction = NewType("Direction", str)


class SubmarineSystem:
    serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    def __init__(self) -> None:
        """The system for handling submarines."""

        self._submarines: dict[SerialNumber, self._Submarine] = {}

        # Keeps track of which positions submarines has been moved to, so that we can log if another submarine is sent to the same position (collision)
        self._occupied_positions: dict[tuple, bool] = {}
        self._collided_submarines: list[SubmarineInfo] = []

    @property
    def submarines(self) -> Generator[SerialNumber]:
        for k in self._submarines:
            yield k

    @property
    def max_move_logs(self) -> int:
        """The maximum amount of movement log entries a submarine can have."""
        return self._Submarine.max_move_logs

    @property
    def collided_submarines(self) -> list[SubmarineInfo]:
        """Current list of submarines that have collided."""

        return self._collided_submarines
    
    def _get_sub(self, serial_number: SerialNumber) -> "SubmarineSystem._Submarine":
        return self._submarines.get(serial_number)

    def lookup_submarine(self, serial_number: SerialNumber) -> Optional[SubmarineInfo]:
        """Get a submarine by serial number if it exists."""

        sub = self._get_sub(serial_number)

        if sub is None:
            return None
        else:
            return str( sub )
    
    def register_submarine(self, serial_number: SerialNumber) -> None:
        """Register a submarine of given 'serial_number'."""

        if not self.serial_number_pattern.match(serial_number):
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")

        if not self._get_sub(serial_number) is None:
            print(f"Warning: Submarine {serial_number} already registered! Overwriting.")

        # Create new submarine
        self._submarines[serial_number] = self._Submarine(serial_number)
    
    def clear_submarines(self) -> None:
        """Removes all registered submarines."""
        self._submarines.clear()

    def activate_nuke(self, serial_number: SerialNumber, auth_string: str) -> None:
        """
        Activate the nuke for the supplied submarine.
        Will fail if the user is not authenticated.
        """

        sha = hashlib.sha256( auth_string.encode() )
        sub = self._get_sub(serial_number)
        success = sub.ready_nuke(sha.hexdigest())

        if success:
            print(f"Successfully activated nuke for {sub}!")
        else:
            print(f"Could not ready nuke for {sub}, wrong auth string!")
 
    @staticmethod
    def _prevent_friendly_fire(func: Callable) -> Callable:
        """Prevents friendly fire when ordering a torpedo."""

        def wrapper(system: "SubmarineSystem", serial_number: SerialNumber, dir: Direction) -> Union[bool, SubmarineInfo]:
            friendly_fire = False
            firing_sub = system._get_sub(serial_number)

            match dir:
                case "up":
                    for _, sub in system._submarines.items():
                        if sub==firing_sub: continue
                        if firing_sub.position[1] == sub.position[1] and sub.position[0] >= firing_sub.position[0]:
                            friendly_fire = True
                            break
                case "down":
                    for _, sub in system._submarines.items():
                        if sub==firing_sub: continue
                        if firing_sub.position[1] == sub.position[1] and sub.position[0] <= firing_sub.position[0]:
                            friendly_fire = True
                            break
                case "forward":
                    for _, sub in system._submarines.items():
                        if sub==firing_sub: continue
                        if firing_sub.position[0] == sub.position[0] and sub.position[1] >= firing_sub.position[1]:
                            friendly_fire = True
                            break
            
            if friendly_fire:
                return sub
            else:
                return func(system, serial_number, dir)

        return wrapper
    
    @_prevent_friendly_fire # This can cause this function to return SubmarineInfo instead of bool
    def order_torpedo(self, serial_number: SerialNumber, dir: Direction) -> Union[bool, SubmarineInfo]:
        """
        Orders a submarine to fire a torpedo to the location.

        Will not fire if it would hit another submarine.
        Returns the submarine it would've hit in that case.
        """

        sub = self._get_sub(serial_number)

        if sub is None:
            raise LookupError(f"Submarine '{serial_number}' not found.")

        sub.fire_torpedo(dir)
        return True
    
    def torpedo_graphic(self) -> None:
        """Fancy torpedo graphics!!"""
        for _ in range(3):
            steps = 40
            for i in range(steps):
                print(" "*(steps-i) + "c=={ "+"-"*i, end="\r")
                time.sleep(0.02)
            print()
        
    def count_sensor_errors(self, serial_number: SerialNumber) -> SensorErrorList:
        """
        Returns a list of all types of sensor errors that occured,
        how many times they occured,
        and how many sensors that failed during said error/errors.
        """

        if not os.path.isdir("Sensordata"):
            raise FileNotFoundError("No 'Sensordata' directory detected.")
        
        sub = self._get_sub(serial_number)
        if sub is None:
            raise LookupError(f"Submarine '{serial_number}' not found.")

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

        if sub is None:
            raise LookupError(f"Submarine '{serial_number}' not found.")
        
        return sub.movement_log
    
    def get_submarine_count_by_movement_reports(self) -> int:
        """Gets how many submarines are listed in the movement reports."""

        if not os.path.isdir("MovementReports"):
            raise FileNotFoundError("No 'MovementReports' directory detected.")
        
        list_dir = os.listdir("MovementReports")
        return len(list_dir)
        
    def register_submarines_by_movement_reports(self):
        """
        Register submarines by movement reports.
        """

        if not os.path.isdir("MovementReports"):
            raise FileNotFoundError("No 'MovementReports' directory detected.")

        list_dir = os.listdir("MovementReports")
        for file_name in list_dir:
            serial_number = Path(file_name).stem
            self.register_submarine(serial_number)

    @staticmethod
    def _collision_logger(func: Callable) -> Callable:
        """Logs collisions between submarines."""

        def wrapper(system: "SubmarineSystem", serial_number: SerialNumber):
            return_value = func(system, serial_number)

            sub = system._get_sub(serial_number)
            pos = (sub.position[0], sub.position[1])

            if system._occupied_positions.get(pos):
                system._collided_submarines.append(sub)
                print(f"Warning: {sub} has collided with another submarine!")
            else:
                system._occupied_positions[pos] = True

            return return_value
        
        return wrapper
    
    @_collision_logger
    def move_submarine_by_reports(self, serial_number: SerialNumber) -> None:
        """Read movement reports for this submarine, and move it accordingly"""

        sub = self._get_sub(serial_number)

        if sub is None:
            raise LookupError(f"Submarine '{serial_number}' not found.")

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

    @staticmethod
    def _safe_sort_subs(func: Callable) -> Callable:
        def wrapper(system: "SubmarineSystem"):
            if len(system._submarines) == 0:
                raise ValueError("No submarines registered.")
            
            return func(system)

        return wrapper
    
    @_safe_sort_subs
    def _get_subs_sorted_dist(self) -> list["_Submarine"]:
        """Get submarines sorted by distance from the base."""

        return sorted(self._submarines.values(), key=lambda submarine: submarine.dist_from_base)

    @_safe_sort_subs
    def _get_subs_sorted_vertical(self) -> list["_Submarine"]:
        """Get submarines sorted by altetude from the base."""

        return sorted(self._submarines.values(), key=lambda submarine: submarine.position[0])

    class _Submarine:
        max_move_logs = 50

        def __init__(self, serial_number: SerialNumber) -> None:
            self._serial_number: SerialNumber = serial_number
            self._position: Position = Position([0, 0])
            self._movement_log: MovementLog = deque(maxlen=self.max_move_logs)

        def fire_torpedo(self, _: Direction) -> None:
            """Torpedo firing logic here..."""

        def _find_my_secret_key(self) -> str:
            with open("Secrets/SecretKEY.txt") as f:
                for line in f:
                    split = line.split(":")
                    
                    if split[0] == self.serial_number:
                        return split[1].strip("\n")
                    
            raise LookupError(f"Could not find {self} secret key.")
        
        def _find_my_activation_code(self) -> str:
            with open("Secrets/ActivationCodes.txt") as f:
                for line in f:
                    split = line.split(":")

                    if split[0] == self.serial_number:
                        return split[1].strip("\n")
                    
            raise LookupError(f"Could not find {self} activation code.")

        def ready_nuke(self, hex_str: str) -> bool:
            if not os.path.isfile("Secrets/ActivationCodes.txt"):
                raise FileNotFoundError("'ActivationCodes.txt' not found.")
            
            if not os.path.isfile("Secrets/SecretKEY.txt"):
                raise FileNotFoundError("'SecretKEY.txt' not found.")

            date_now_str = str( date.today() )
            key = self._find_my_secret_key()
            code = self._find_my_activation_code()
            combined_string = date_now_str+key+code
            sha = hashlib.sha256( combined_string.encode() )

            # Ready nuke logic here...

            return sha.hexdigest()==hex_str
            
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
            def wrapper(sub: "SubmarineSystem._Submarine", dir: str, dist: int):
                old_pos = (sub.position[0], sub.position[1])
                
                return_value = func(sub, dir, dist)

                new_pos = (sub.position[0], sub.position[1])
                
                log_entry: MovementLogEntry = (old_pos, dir, dist, new_pos)
                sub._movement_log.append(log_entry)

                return return_value

            return wrapper

        @_log_movement
        def move(self, dir: Direction, dist: int) -> None:
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



if __name__ == "__main__":
    """Submarine system showcase!"""

    system: SubmarineSystem = SubmarineSystem()
    system.register_submarines_by_movement_reports()
    submarine_test_limit = ( len(sys.argv) >= 2 and int( sys.argv[1] ) or system.get_submarine_count_by_movement_reports())


    class _Colors(Enum):
        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKCYAN = "\033[96m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"
        ITALIC = "\033[3m"


    def _pretty_print(text: str, color: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                print(color + text)

                return_value = func(*args, **kwargs)
                
                print("-" * 20 + _Colors.ENDC.value)

                return return_value
            
            return wrapper
        return decorator
    

    @_pretty_print("Moving submarine by reports...", _Colors.ITALIC.value)
    def _move_submarines() -> SerialNumber:
        for serial_number, i in zip( system.submarines, range(submarine_test_limit) ):
            system.move_submarine_by_reports(serial_number)
            print(f"{i+1}/{submarine_test_limit} movement reports progress...")
        return serial_number
    

    @_pretty_print("Counting sensor errors...", _Colors.ITALIC.value)
    def _count_sensor_errors() -> tuple[SerialNumber, SensorErrorList]:
        for serial_number, i in zip( system.submarines, range(submarine_test_limit) ):
            sensor_errors: SensorErrorList = system.count_sensor_errors(serial_number)
            print(f"{i+1}/{submarine_test_limit} sensor error progress...")  
        return serial_number, sensor_errors


    @_pretty_print("Showing sensor errors for 1 submarine...", _Colors.FAIL.value)
    def _show_sensor_errors(serial_number: SerialNumber, sensor_errors: SensorErrorList) -> None:
        entries = 50

        print(system.lookup_submarine(serial_number), f"sensor errors (showing {entries}/{len(sensor_errors)} entries):")
        for error, i in zip(sensor_errors, range(1, entries+1)):
            print(f"Error type {i}: {error}", end=i%2==0 and "\n" or ", ")
        print()

        print("^^^^^^^^^^^ Sensor error log")


    @_pretty_print("Showing movement log for 1 submarine...", _Colors.OKCYAN.value)
    def _show_movement_log(serial_number: SerialNumber) -> None:
        print(f"{system.lookup_submarine(serial_number)} ({system.max_move_logs} entries)")
        
        movement_log: MovementLog = system.get_submarine_movement_log(serial_number)
        for entry in movement_log:
            print(entry)
        
        print("^^^^^^^^^^^ Movement log")


    @_pretty_print("Misc location info:", _Colors.OKBLUE.value)
    def _show_location_info() -> None:
        closest: SubmarineInfo = system.get_closest_submarine()
        furthest: SubmarineInfo = system.get_furthest_submarine()
        highest: SubmarineInfo = system.get_highest_submarine()
        lowest: SubmarineInfo = system.get_lowest_submarine()

        print(f"Closest: {closest}, furthest: {furthest}, highest: {highest}, lowest: {lowest}")


    @_pretty_print("List of subs that collided:", _Colors.WARNING.value)
    def _show_collisions() -> None:
        if len(system.collided_submarines) == 0:
            print("None.")
            return

        for info in system.collided_submarines:
            print(info)

        print("^^^^^^^^^^^ Collision log")


    @_pretty_print("Ordering torpedos...", _Colors.BOLD.value)
    def _order_random_torpedos() -> None:
        system.torpedo_graphic()

        torpedo_failures = 0
        torpedo_failure_prints = 0
        max_torpedo_failure_prints = 50
        for serial_number, _ in zip( system.submarines, range(submarine_test_limit) ):
            direction = random.choice(("up", "down", "forward"))
            return_value = system.order_torpedo(serial_number, direction)

            if not return_value is True:
                torpedo_failures+=1
                if torpedo_failure_prints < max_torpedo_failure_prints:
                    print(f"{system.lookup_submarine(serial_number)} fire torpedo failed {direction} - friendly fire towards {return_value}!")
                    torpedo_failure_prints += 1
        
        if torpedo_failure_prints < torpedo_failures:
            print(f"{torpedo_failures-torpedo_failure_prints} other submarines failed firing torpedos!")

        print(f"{submarine_test_limit-torpedo_failures} torpedos fired successfully!")


    @_pretty_print("TESTING NUKES!", _Colors.WARNING.value)
    def _test_nukes(serial_number: SerialNumber, auth_string: str) -> None:
        sub: SubmarineInfo = system.lookup_submarine(serial_number)

        if sub is None:
            raise LookupError(f"Could not find submarine with serial number '{serial_number}'.")
        
        print(f"Testing on {sub}...")
        print(f"Trying to authenticate with '{auth_string}'...")

        time.sleep(2)

        system.activate_nuke(serial_number, auth_string)


    sub_sn_sensor_test, sensor_errors = _count_sensor_errors()
    sub_sn_movelog_test = _move_submarines()

    _show_sensor_errors(sub_sn_sensor_test, sensor_errors)
    time.sleep(1)

    _show_movement_log(sub_sn_movelog_test)
    time.sleep(1)

    _show_collisions()
    time.sleep(1)
    
    _show_location_info()
    time.sleep(1)

    _order_random_torpedos()
    time.sleep(2)

    date_now_str = str( date.today() )
    secret_key = "Vvkn0pAqXmGEeNRAj2h03C3vI2x"
    activation_code = "RpojkncM1F1rr9xiiE"
    _test_nukes("41158662-03", date_now_str+secret_key+activation_code)

    time.sleep(2)
    print("Scroll up to see full showcase!")
