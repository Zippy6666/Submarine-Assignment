from typing import NewType, Optional
import re, os, time, random, shutil


SerialNumber = NewType("SerialNumber", str)
Position = NewType("Position", list)


class Submarine:
    def __init__(
        self, system: "SubmarineSystem", serial_number: SerialNumber, sensors:list[str]
    ) -> None:
        """A submarine."""
        self._serial_number: SerialNumber = serial_number
        self._position: Position = Position([0, 0])
        self._sensors: list[str] = sensors
        self._system: SubmarineSystem = system

    @property
    def serial_number(self) -> SerialNumber:
        return self._serial_number

    @property
    def sensors(self):
        return self._sensors
    
    @property
    def dist_from_base(self):
        return ( self._position[0]**2 + self._position[1]**2 ) ** 0.5
    
    def use_sensors(self) -> None:
        # Insert logic here...
        self._system._log_submarine_sensors(self)

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


class SubmarineSystem:
    serial_number_pattern = re.compile(r"^\d{8}-\d{2}$")

    def __init__(self) -> None:
        """The system for handling submarines"""
        self._submarines: dict[SerialNumber, Submarine] = {}
        self._make_dirs()

    def lookup_submarine(self, serial_number: SerialNumber) -> Optional[Submarine]:
        """Get a submarine by serial number if it exists"""
        return self._submarines.get(serial_number)
    
    def get_submarines(self) -> list[Submarine]:
        """ Returns a list of all registered submarines """
        return self._submarines.values()

    def register_submarine(self, serial_number: SerialNumber, sensors: list[str]) -> Submarine:
        """Register or overwrite a submarine of given serial_number"""
        if not self.serial_number_pattern.match(serial_number):
            raise ValueError("Serial number must be in the format XXXXXXXX-XX")
        submarine: Submarine = Submarine(self, serial_number, sensors)
        self._submarines[serial_number] = submarine
        return submarine
    
    def get_furthest_submarine(self) -> Submarine:
        ...

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

    def _log_submarine_sensors(self, sub: Submarine) -> None:
        with open("SensorData/" + sub.serial_number + ".txt", "a") as file:
            file.write("".join(sub.sensors)+"\n")

    def _submarines_sorted_by_distance(self) -> list:
        return sorted(self._submarines.values(), key=lambda submarine: submarine.dist_from_base)

    def _submarines_sorted_by_vertical_distance(self) -> list:
        raise NotImplementedError


def simulate(system: SubmarineSystem) -> None:
    """ Simulates the movements and sensors of the submarines """
    for sub in system.get_submarines():
        # Move submarines randomly
        if random.randint(1, 2)==1:
            sub.move(random.choice(("up", "down", "left", "right")), random.randint(1, 10))

        # Break sensors randomly
        if random.randint(1, 4)==1:
            sub.sensors[random.randint(0, 207)] = "0"
            
        # Use sensors, this will log sensor data
        sub.use_sensors()
    

def main() -> None:
    """ Submarine simulation """
    shutil.rmtree("SensorData", ignore_errors=True) # Clear sensordata

    system: SubmarineSystem = SubmarineSystem()

    # Register some example submarines
    print("Generating example submarines...")
    submarine_count: int = 3000
    for i in range(submarine_count):
        serial_number: SerialNumber = SerialNumber(
            f"1234{i:04}-42"
        )
        # Create a submarine with all sensors working
        system.register_submarine(serial_number, ["1" for _ in range(208)])
    print(submarine_count, "submarines created!")


    print("Simulating submarines...")
    while True:
        simulate(system)
        time.sleep(1)
        print("One iteration simulated!")


if __name__ == "__main__":
    main()
