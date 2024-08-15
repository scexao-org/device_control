import time

import elliptec

from device_control.base import ConfigurableDevice

"""
Please refer to this github repo for the detailed information about the Elliptec package:
https://github.com/roesel/elliptec
"""


class ThorlabsElliptec(ConfigurableDevice):
    FORMAT_STR = "{0}: {1} {{{2}}}"

    def __init__(self, serial_kwargs, unit=None, **kwargs):
        serial_kwargs = dict({"baudrate": 9600, "rtscts": True}, **serial_kwargs)
        self.controller = elliptec.Controller(serial_kwargs["port"], debug=False)
        ser_type = serial_kwargs.pop("type").lower()
        if ser_type == "rotator":
            self.device = elliptec.Rotator(self.controller)
        elif ser_type == "shutter":
            self.device = elliptec.Shutter(self.controller)
        elif ser_type == "slider":
            self.device = elliptec.Slider(self.controller)
        elif ser_type == "linear":
            self.device = elliptec.Linear(self.controller)
        self.unit = unit
        super().__init__(serial_kwargs=serial_kwargs, **kwargs)

    def _config_extras(self):
        return {"unit": self.unit}

    def get_unit(self):
        return self.unit

    def set_unit(self, value):
        self.unit = value

    def update_keys(self, position=None):
        if position is None:
            position = self.get_position()
        self.logger.info("%s unit=%s", position, self.unit)
        return self._update_keys(position)

    def _update_keys(self, position):
        raise NotImplementedError()

    # @autoretry
    def set_position(self, position: float):
        self.logger.debug("MOVING to=%s unit=%s", position, self.unit)
        self.device.set_angle(position)
        time.sleep(1)
        self.update_keys()

    # @autoretry
    def get_position(self):
        result = self.device.get_angle()
        self.logger.debug("RECEIVED position=%s", result)
        time.sleep(0.1)
        self.update_keys(result)
        return result

    def move_relative(self, value):
        self.logger.debug("MOVING relative=%s unit=%s", value, self.unit)
        self.device.shift_angle(value)
        result = self.device.get_angle()
        self.update_keys(result)
        return result

    def home(self):
        self.logger.debug("HOMING")
        self.device.home()

    def move_configuration(self, idx_or_name, **kwargs):
        if isinstance(idx_or_name, int) or idx_or_name.isdigit():
            return self.move_configuration_idx(int(idx_or_name), **kwargs)

        return self.move_configuration_name(idx_or_name, **kwargs)

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
