from serial import Serial
import tomli

class ThorlabsWheel:

    def __init__(self, address, name="", configurations=None, config_file=None, **kwargs):
        self._address = address
        self._name = name
        self._configurations = configurations
        self.config_file = config_file
        self.serial = Serial(
            port=self.address,
            baudrate=115200,
            # timeout=0.5,
            **kwargs
        )

    @property
    def configurations(self):
        return self._configurations

    @configurations.setter
    def configurations(self, value):
        self._configurations = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value: str):
        self._address = value


    @classmethod
    def from_config(__cls__, filename):
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        configurations = parameters.pop("configurations", None)
        return __cls__(configurations=configurations, config_file=filename, **parameters)

    def load_config(self, filename=None):
        if filename is None:
            filename = self.config_file
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        self.address = parameters["address"]
        self.name = parameters["name"]
        self.unit = parameters.get("unit", None)
        self.configurations = parameters.get("configurations", None)
        self.config_file = filename

    def send_command(self, cmd: str):
        with self.serial as serial:
            serial.write(cmd.encode())
            serial.read_until(b"\r")

    def ask_command(self, cmd: str):
        with self.serial as serial:
            serial.write(cmd.encode())
            serial.read_until(b"\r")
            return serial.read_until(b"\r").decode().strip()

    def move_configuration(self, index, wait=False):
        if self.configurations is None:
            raise ValueError("No configurations saved")
        if isinstance(index, int):
            return self.move_configuration_idx(index, wait=wait)
        elif isinstance(index, str):
            return self.move_configuration_name(index, wait=wait)

    def move_configuration_idx(self, idx: int, wait=False):
        self.send_command(f"pos={idx}\r")

    def move_configuration_name(self, name: str, wait=False):
        for row in self.configurations:
            if row["name"].lower() == name.lower():
                return self.move_configuration_idx(row["idx"], wait=wait)
        raise ValueError(f"No configuration saved with name '{name}'")

    def position(self):
        result = self.ask_command("pos?\r")
        return int(result)

    def status(self):
        idx = self.position()
        for row in self.configurations:
            if row["idx"] == idx:
                return row["name"]
        return "Unknown"

    def id(self):
        result = self.ask_command("*idn?\r")
        return result

    def speed(self):
        result = self.ask_command("speed?\r")
        if result == "0":
            return "Slow speed (0)"
        elif result == "1":
            return "High speed (1)"

    def sensors(self):
        result = self.ask_command("sensors?\r")
        if result == "0":
            return "Off when idle (0)"
        elif result == "1":
            return "Always on (1)"
        
    def trig(self):
        result = self.ask_command("trig?\r")
        if result == "0":
            return "Input mode (0)"
        elif result == "1":
            return "Output mode (1)"
        
    def count(self):
        result = self.ask_command("pcount?\r")
        return int(result)