# interface for USB arduinos
import tomli
from dataclasses import dataclass
from serial import Serial

@dataclass
class USBArduino:
    address: str
    name: str = None
    config_file: str = None

    def __post_init__(self, **kwargs):
        self.serial = Serial(
            self.address,
            baudrate=115200
        )


    @classmethod
    def from_config(__cls__, filename):
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)

        return __cls__(
            address=parameters["address"],
            timing_info=parameters["timing"],
            config_file=filename
        )

    def load_config(self, filename=None):
        if filename is None:
            filename = self.config_file
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        
        self.address = parameters["address"]
        self.config_file = filename

    def send_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())

    def ask_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())
            return serial.readlines()