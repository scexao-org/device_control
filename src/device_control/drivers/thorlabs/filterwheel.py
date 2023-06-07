from device_control.base import MotionDevice
import re
from swmain.autoretry import autoretry
import time


class ThorlabsWheel(MotionDevice):
    def __init__(self, serial_kwargs, **kwargs):
        serial_kwargs = dict(
            {"baudrate": 115200, "timeout": 0.5},
            **serial_kwargs,
        )
        super().__init__(serial_kwargs=serial_kwargs, **kwargs)
        self.max_filters = 6  # self.get_count()

    @autoretry
    def send_command(self, cmd: str):
        with self.serial as serial:
            serial.reset_input_buffer()
            serial.write(f"{cmd}\r".encode())
            line = serial.readline()
            res = re.search(".+\r", line.decode())
            print(res.group(0))
            assert res.group(0).strip() == cmd

    @autoretry
    def ask_command(self, cmd: str):
        with self.serial as serial:
            serial.reset_input_buffer()
            serial.write(f"{cmd}\r".encode())
            line = serial.readline()
            res = re.search("(.+)\r", line.decode())
            cmd, val = res.group(0).split()
            print(f"cmd: {cmd}")
            print(f"val: {val}")
            # return res.group(1)
            return val

    def _get_position(self):
        result = self.ask_command("pos?")
        return int(result)

    def _move_absolute(self, value, **kwargs):
        if value < 1 or value > self.max_filters:
            raise ValueError(f"Filter position must be between 1 and {self.max_filters}")
        self.send_command(f"pos={value}")
        time.sleep(1)

    def get_status(self, idx=None):
        if idx is None:
            idx = self.get_position()
        for row in self.configurations:
            if row["idx"] == idx:
                return row["name"]
        return "Unknown"

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
