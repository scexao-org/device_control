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
    tint: Union[float, int, u.Quantity] = 2 * u.ms
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
            self.tint = self.tint.to(u.us).value

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
        cmd = "1 {:.0f} {:.0f} {:.0f} {:.0f}".format(
            self.tint,
            self.pulse_width,
            self.flc_offset,
            trigger_mode
        )
        self.send_command(cmd)

    def set_tint(self, tint):
        if isinstance(tint, u.Quantity):
            tint_us = tint.to(u.us).value
        else:
            # tint in ms to us
            tint_us = int(tint * 1e3)
        self.tint = tint_us
        self.set_timing_info()

    def disable(self):
        self.send_command(2)

    def enable(self):
        self.send_command(3)
        # update_keys(
        #     U_FLCEN="ON" if self.timing_info["flc_enabled"] else "OFF",
        #     U_FLCDL=self.timing_info["flc_offset"],
        #     U_FLCJT=self.timing_info["flc_jitter"],
        #     U_FLCTM=self.timing_info["pulse_width"]
        # )

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
        # update_keys(U_FLCEN="ON" if info["flc_enabled"] else "OFF")
        return info
