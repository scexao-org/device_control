import numpy as np

from device_control.base import MotionDevice
from swmain.autoretry import autoretry


class ThorlabsWheel(MotionDevice):
    def __init__(self, serial_kwargs, **kwargs):
        serial_kwargs = dict(
            {"baudrate": 115200, "timeout": None},
            **serial_kwargs,
        )
        super().__init__(serial_kwargs=serial_kwargs, **kwargs)
        self.max_filters = 6  # self.get_count()

    # @autoretry
    def send_command(self, cmd: str):
        with self.serial as serial:
            serial.write(f"{cmd}\r".encode())
            cmd_resp = serial.read_until(b"\r")
            assert cmd_resp.strip().decode() == cmd
            serial.read_until(b"> ")

    # @autoretry
    def ask_command(self, cmd: str):
        with self.serial as serial:
            serial.write(f"{cmd}\r".encode())
            cmd_resp = serial.read_until(b"\r")
            assert cmd_resp.strip().decode() == cmd
            resp = serial.read_until(b"\r")
            serial.read_until(b"> ")
        return resp.strip().decode()

    def _get_position(self):
        return int(self.ask_command("pos?"))

    def _move_absolute(self, value):
        if value < 1 or value > self.max_filters:
            raise ValueError(f"Filter position must be between 1 and {self.max_filters}")
        self.send_command(f"pos={value}")

    def get_status(self):
        posn = self.get_position()
        idx, config = self.get_configuration(posn)
        output = self.format_str.format(idx, config)
        return posn, output

    def get_id(self):
        result = self.ask_command("*idn?")
        return result

    def get_speed(self):
        result = self.ask_command("speed?")
        if result == "0":
            return "Slow speed (0)"
        elif result == "1":
            return "High speed (1)"

    def get_sensors(self):
        result = self.ask_command("sensors?")
        if result == "0":
            return "Off when idle (0)"
        elif result == "1":
            return "Always on (1)"

    def get_trig(self):
        result = self.ask_command("trig?")
        if result == "0":
            return "Input mode (0)"
        elif result == "1":
            return "Output mode (1)"

    def get_count(self):
        result = self.ask_command("pcount?")
        return int(result)
