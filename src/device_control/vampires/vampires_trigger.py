import tomli
from typing import Union
import numpy as np
from serial import Serial
from dataclasses import dataclass

# from swmain.redis import update_keys


@dataclass
class VAMPIRESTrigger:
    address: str
    timing_info: dict
    config_file=None

    def __post_init__(self, **kwargs):
        self.serial = Serial(
            self.address,
            baudrate=115200,
            write_timeout=0.5
        )

    def send_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())

    def ask_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())
            return serial.readline()

    def get_timing_info(self):
        resp = self.ask_command(0)
        tokens = resp.split()
        return {
            "enabled": bool(tokens[0]),
            "integration_time": int(tokens[1]),
            "pulse_width": int(tokens[2]),
            "flc_offset": int(tokens[3]),
            "trigger_mode": int(tokens[4]),
        }

    def set_timing_info(self, timing_info=None):
        if timing_info is None:
            timing_info = self.timing_info
        cmd = "1 {:d} {:d} {:d} {:d}".format(
            timing_info["integration_time"],
            timing_info["pulse_width"],
            timing_info["flc_offset"],
            timing_info["trigger_mode"],
        )
        self.send_command(cmd)

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

    def disable_flc(self):
        self.send_command(4)
        # update_keys(U_FLCEN="OFF")

    def enable_flc(self):
        self.send_command(5)
        # update_keys(U_FLCEN="ON")

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
        self.timing_info = parameters["timing"]
        self.config_file = filename

    def status(self):
        info = self.get_timing_info()
        # update_keys(U_FLCEN="ON" if info["flc_enabled"] else "OFF")
        return info
