import tomli
from typing import Union
import numpy as np
from serial import Serial
from dataclasses import dataclass
import astropy.units as u

# from swmain.redis import update_keys


@dataclass
class VAMPIRESTrigger:
    address: str
    tint: int = 2000 # us
    pulse_width: int = 10 # us
    flc_offset: int = 20 # us
    flc_enabled: bool = True
    sweep_mode: bool = False
    config_file=None

    def __post_init__(self, **kwargs):
        self.serial = Serial(
            self.address,
            baudrate=115200,
            write_timeout=0.5
        )
        if isinstance(self.tint, u.Quantity):
            self.tint = int(self.tint.to(u.us).value)
        if isinstance(self.pulse_width, u.Quantity):
            self.pulse_width = int(self.pulse_width.to(u.us).value)
        if isinstance(self.flc_offset, u.Quantity):
            self.flc_offset = int(self.flc_offset.to(u.us).value)

    @tint.setter
    def tint(self, value):
        if isinstance(value, u.Quantity):
            self.tint = int(self.tint.to(u.us).value)
        else:
            self.tint = int(value)

    @pulse_width.setter
    def pulse_width(self, value):
        if isinstance(value, u.Quantity):
            self.pulse_width = int(self.pulse_width.to(u.us).value)
        else:
            self.pulse_width = int(value)

    @flc_offset.setter
    def flc_offset(self, value):
        if isinstance(value, u.Quantity):
            self.flc_offset = int(self.flc_offset.to(u.us).value)
        else:
            self.flc_offset = int(value)

    def send_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())

    def ask_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())
            return serial.readline()

    def get_parameters(self):
        resp = self.ask_command(0)
        tokens = resp.split()
        enabled = bool(tokens[0])
        self.tint = int(tokens[1])
        self.pulse_width = int(tokens[2])
        self.flc_offset = int(tokens[3])
        trigger_mode = int(tokens[4])
        self.flc_enabled = trigger_mode & 0x1
        self.sweep_mode = trigger_mode & 0x2
        # self.update_keys()
        return {
            "enabled": enabled,
            "integration_time": self.tint,
            "pulse_width": self.pulse_width,
            "flc_offset": self.flc_offset,
            "flc_enabled": self.flc_enabled,
            "sweep_mode": self.sweep_mode,
        }

    def set_parameters(self):
        trigger_mode = int(self.flc_enabled) + (int(self.sweep_mode) << 1)
        cmd = "1 {:d} {:d} {:d} {:d}".format(
            self.tint,
            self.pulse_width,
            self.flc_offset,
            trigger_mode
        )
        result = self.ask_command(cmd)
        if result != "OK":
            raise ValueError(result)
        # self.update_keys()

    def set_tint(self, tint):
        self.tint = tint
        self.set_parameters()

    def disable(self):
        self.send_command(2)

    def enable(self):
        self.send_command(3)

    # def update_keys(self):
    #     update_keys(
    #         U_FLCEN="ON" if self.flc_enabled else "OFF",
    #         U_FLCOFF=self.flc_offset,
    #         U_TRIGPW=self.pulse_width
    #     )

    @classmethod
    def from_config(__cls__, filename):
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)

        return __cls__(
            config_file=filename,
            **parameters,
        )

    def load_config(self, filename=None):
        if filename is None:
            filename = self.config_file
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        
        self.address = parameters["address"]
        self.pulse_width = parameters.get("pulse_width", self.pulse_width)
        self.flc_offset = parameters.get("flc_offset", self.flc_offset)
        self.config_file = filename

    def status(self):
        info = self.get_timing_info()
        # self.update_keys()
        return info
