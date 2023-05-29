import numpy as np
import tomli
from serial import Serial
import time

from device_control.base import ConfigurableDevice

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


class ThorlabsFlipMount(ConfigurableDevice):
    def __init__(self, serial_kwargs, **kwargs):
        serial_kwargs = dict({"baudrate": 115200, "rtscts": True}, **serial_kwargs)
        super().__init__(serial_kwargs=serial_kwargs, **kwargs)

    def set_position(self, position: str):
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
        self.update_keys()

    def get_position(self):
        with self.serial as serial:
            serial.write(COMMANDS["status"])
            time.sleep(20e-3)
            response = serial.read(12)
        if response == STATUSES["down"]:
            result = "DOWN"
        elif response == STATUSES["up"]:
            result = "UP"
        else:
            result = "Unknown"
        self.update_keys(result)
        return result
