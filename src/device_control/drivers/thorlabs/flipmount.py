from serial import Serial
import tomli
import numpy as np


# Raw byte commands for "MGMSG_MOT_MOVE_JOG"
COMMANDS = {
    "up": b"\x6A\x04\x00\x01\x21\x01",
    "down": b"\x6A\x04\x00\x02\x21\x01",
    "status": b"\x29\x04\x00\x00\x21\x01",
}

STATUSES = {
    "up": b"*\x04\x06\x00\x81P\x01\x00\x01\x00\x00\x90",
    "down": b"*\x04\x06\x00\x81P\x01\x00\x02\x00\x00\x90",
}


class ThorlabsFlipMount:
    def __init__(
        self, address, configurations=None, name="", config_file=None, **kwargs
    ):
        self._address = address
        self._name = name
        self.config_file = config_file
        self._configurations = configurations
        self.serial = Serial(
            port=self.address,
            baudrate=115200,
            rtscts=True,
            **kwargs,
        )

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

    @property
    def configurations(self):
        return self._configurations

    @configurations.setter
    def configurations(self, value):
        self._configurations = value

    @classmethod
    def from_config(__cls__, filename):
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        configurations = parameters.pop("configurations", None)

        return __cls__(
            configurations=configurations, config_file=filename, **parameters
        )

    def load_config(self, filename=None):
        if filename is None:
            filename = self.config_file
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        self._config_file = filename
        self._address = parameters["address"]
        self._name = parameters.get("name", "")
        self._configurations = parameters.get("configurations", None)

    def move_configuration(self, name: str):
        for row in self.configurations:
            if row["name"].lower() == name.lower():
                return self.flip(row["idx"])
        raise ValueError(f"No configuration saved with name '{name}'")

    def flip(self, position: str):
        if position.lower() == "down":
            cmd = COMMANDS["down"]
        elif position.lower() == "up":
            cmd = COMMANDS["up"]
        else:
            raise ValueError(
                f"Position should be either 'up' or 'down', got '{position}'"
            )

        with self.serial as serial:
            serial.write(cmd)

    @property
    def position(self):
        with self.serial as serial:
            serial.write(COMMANDS["status"])
            result = serial.read(12)
        if result == STATUSES["down"]:
            return "DOWN"
        elif result == STATUSES["up"]:
            return "UP"
        return "Unknown"

    def get_configuration(self):
        position = self.position
        for row in self.configurations:
            if row["idx"].lower() == position.lower():
                return row["idx"], row["name"]
        return None, "Unknown"
