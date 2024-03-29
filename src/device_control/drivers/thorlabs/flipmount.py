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

    def update_keys(self, position=None):
        if position is None:
            position = self.get_position()
        return self._update_keys(position)

    def _update_keys(self, position):
        raise NotImplementedError()

    # @autoretry
    def set_position(self, position: str):
        if position.lower() == "down":
            cmd = COMMANDS["down"]
        elif position.lower() == "up":
            cmd = COMMANDS["up"]
        else:
            msg = f"Position should be either 'up' or 'down', got '{position}'"
            raise ValueError(msg)

        with self.serial as serial:
            serial.write(cmd)
            time.sleep(1)
        self.update_keys()

    # @autoretry
    def get_position(self):
        with self.serial as serial:
            serial.write(COMMANDS["status"])
            time.sleep(0.1)
            response = serial.read(12)
        if response == STATUSES["down"]:
            result = "down"
        elif response == STATUSES["up"]:
            result = "up"
        else:
            result = "unknown"
        self.update_keys(result)
        return result

    def move_configuration_idx(self, idx: int):
        for row in self.configurations:
            if row["idx"] == idx:
                return self.set_position(row["value"])
        msg = f"No configuration saved at index {idx}"
        raise ValueError(msg)

    def move_configuration_name(self, name: str):
        for row in self.configurations:
            if row["name"].lower() == name.lower():
                return self.set_position(row["value"])
        msg = f"No configuration saved with name '{name}'"
        raise ValueError(msg)

    def get_configuration(self, position=None):
        if position is None:
            position = self.get_position()
        for row in self.configurations:
            if position == row["value"]:
                return row["idx"], row["name"]
        return None, "Unknown"

    def get_status(self):
        posn = self.get_position()
        idx, config = self.get_configuration(posn)
        output = self.format_str.format(idx, config)
        return posn, output
