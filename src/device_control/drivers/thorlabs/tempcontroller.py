from serial import Serial
import tomli


def parse_status(bytevalues):
    statbits = int(bytevalues, base=16)
    output = {
        "enabled": bool(statbits & 0b1),
        "mode": statbits & 0b10,
        "alarm": bool(statbits & 0b1000000),
        "paused": bool(statbits & 0b10000000),
    }
    if statbits & 0b10000:
        output["unit"] = "C"
    elif statbits & 0b100000:
        output["unit"] = "F"
    else:
        output["unit"] = "K"
    return output


class ThorlabsTC:
    def __init__(self, address, name="", config_file=None, **kwargs):
        self._address = address
        self._name = name
        self.config_file = config_file
        self.serial = Serial(
            port=self.address,
            baudrate=115200,
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
        self.unit = parameters.get("unit", None)
        self.config_file = filename

    def send_command(self, cmd: str):
        with self.serial as serial:
            serial.write(f"{cmd}\r".encode())
            serial.read_until(b"\r")

    def ask_command(self, cmd: str):
        with self.serial as serial:
            serial.write(f"{cmd}\r".encode())
            serial.read_until(b"\r")
            return serial.read_until(b"\r").decode().strip()

    @property
    def target(self):
        result = self.ask_command("tset?")
        return float(result.split()[0])

    @target.setter
    def target(self, value: float):
        self.send_command(f"tset={value:.01f}")

    @property
    def temp(self):
        result = self.ask_command("tact?")
        return float(result.split()[0])

    def status(self):
        with self.serial as serial:
            serial.write(b"stat?\r")
            serial.read_until(b"\r")
            result = serial.read(2)
        return parse_status(result)

    @property
    def id(self):
        result = self.ask_command("*idn?")
        return result

    def enable(self):
        status = self.status()
        if not status["enabled"]:
            self.send_command("ens")

    def disable(self):
        status = self.status()
        if status["enabled"]:
            self.send_command("ens")
