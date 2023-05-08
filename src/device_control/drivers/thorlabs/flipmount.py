from serial import Serial
import tomli


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
    def __init__(self, address, name="", config_file=None, **kwargs):
        self._address = address
        self._name = name
        self.config_file = config_file
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

    @classmethod
    def from_config(__cls__, filename):
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        return __cls__(config_file=filename, **parameters)

    def load_config(self, filename=None):
        if filename is None:
            filename = self.config_file
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        self.address = parameters["address"]
        self.name = parameters["name"]
        self.config_file = filename

    def flip(self, position: str):
        if position.lower() == "in":
            cmd = COMMANDS["down"]
        elif position.lower() == "out":
            cmd = COMMANDS["up"]
        with self.serial as serial:
            serial.write(cmd)

    def status(self):
        with self.serial as serial:
            serial.write(COMMANDS["status"])
            result = serial.read(12)
            if result == STATUSES["down"]:
                return "IN"
            elif result == STATUSES["up"]:
                return "OUT"
            return "Unknown"
