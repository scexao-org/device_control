from device_control.base import SSHDevice
import re


class ImageRotator(SSHDevice):
    def get_status(self):
        status = self.ask_command("imr st")
        lines = status.splitlines()
        status_dict = {}
        for line in lines:
            key, value = re.split(":\s+", line)
            try:
                val = float(value)
            except ValueError:
                val = value
            status_dict[key] = val
        return status_dict

    def get_position(self):
        state = self.get_status()
        return state["stage angle"]

    def move_absolute(self, value):
        self.send_command(f"imr ma {value}")

    def move_relative(self, value: float):
        self.send_command(f"imr mr {value}")
