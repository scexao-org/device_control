import time
import elliptec
from device_control.base import ConfigurableDevice

from swmain.autoretry import autoretry

'''
Please refer to this github repo for the detailed information about the Elliptec package:
https://github.com/roesel/elliptec
'''

class ThorlabsElliptec(ConfigurableDevice):
    def __init__(self, serial_kwargs, **kwargs):
        serial_kwargs = dict({"baudrate": 9600, "rtscts": True}, **serial_kwargs)
        self.controller = elliptec.Controller(serial_kwargs['port'], debug=False)
        if serial_kwargs['type'] == 'Rotator':
            self.device = elliptec.Rotator(self.controller)
        elif serial_kwargs['type'] == 'Shutter':
            self.device = elliptec.Shutter(self.controller)
        elif serial_kwargs['type'] == 'Slider':
            self.device = elliptec.Slider(self.controller)
        elif serial_kwargs['type'] == 'Linear':
            self.device = elliptec.Linear(self.controller)
        del[serial_kwargs['type']]
        self.configurations = kwargs['configurations']
        # super().__init__(serial_kwargs=serial_kwargs, **kwargs)

    def update_keys(self, position=None):
        if position is None:
            position = self.get_position()
        return self._update_keys(position)

    def _update_keys(self, position):
        raise NotImplementedError()

    # @autoretry
    def set_position(self, position: float):
        device = self.device
        device.set_angle(position)
        time.sleep(1)
        self.update_keys()

    # @autoretry
    def get_position(self):
        device = self.device
        result = device.get_angle()
        time.sleep(0.1)
        self.update_keys(result)
        return result

    def move_relative(self, value):
        device = self.device
        device.shift_angle(value)
        result = device.get_angle()
        self.update_keys(result)
        return result

    def move_configuration(self, idx_or_name, **kwargs):
        if isinstance(idx_or_name, int) or idx_or_name.isdigit():
            return self.move_configuration_idx(int(idx_or_name), **kwargs)

        return self.move_configuration_name(idx_or_name, **kwargs)

    def move_configuration_idx(self, idx: int):
        for row in self.configurations:
            if row["idx"] == idx:
                return self.set_position(row["value"])
        raise ValueError(f"No configuration saved at index {idx}")

    def move_configuration_name(self, name: str):
        for row in self.configurations:
            if row["name"].lower() == name.lower():
                return self.set_position(row["value"])
        raise ValueError(f"No configuration saved with name '{name}'")

    def get_configuration(self, position=None):
        if position is None:
            position = self.get_position()
        for row in self.configurations:
            if position == row["value"]:
                return row["idx"], row["name"]
        return None, "Unknown"

    def get_status(self):
        posn = int(self.get_position())
        idx, config = self.get_configuration(posn)
        output = self.format_str.format(idx, config)
        return posn, output

    def home(self):
        device = self.device
        print(device)
        result = device.home()
        time.sleep(1)        
        self.update_keys(result)
        return result
