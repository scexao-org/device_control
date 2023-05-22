from typing import Union

import numpy as np
import tomli

from device_control.drivers.conex import CONEXDevice
from device_control.drivers.zaber import ZaberDevice

__all__ = ["MultiDevice"]

from device_control.base import ConfigurableDevice


class MultiDevice(ConfigurableDevice):
    def __init__(self, devices: dict, **kwargs):
        self.devices = devices
        kwargs["serial_kwargs"] = {}
        super().__init__(**kwargs)

    def get_devices(self):
        return self.devices

    def get_device(self, name):
        return self.devices[name]

    def get_position(self, name):
        return self.devices[name].get_position()

    def move_absolute(self, name, value, **kwargs):
        return self.devices[name].move_absolute(value, **kwargs)

    def move_relative(self, name, value, **kwargs):
        return self.devices[name].move_relative(value, **kwargs)

    def stop(self, name=None):
        if name is None:
            for device in self.devices.values():
                device.stop()
        else:
            self.devices[name].stop()

    @classmethod
    def from_config(__cls__, filename):
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        name = parameters["name"]
        devices = {}
        for device_config in parameters["devices"]:
            device_name = device_config["name"]
            device_config["name"] = f"{name}_{device_name}"
            device_config["serial_kwargs"] = device_config.pop("serial")
            dev_type = device_config.pop("type")
            if dev_type.lower() == "conex":
                device = CONEXDevice(config_file=filename, **device_config)
            elif dev_type.lower() == "zaber":
                device = ZaberDevice(config_file=filename, **device_config)
            else:
                raise ValueError(
                    f"motion stage type not recognized: {device_config['type']}"
                )
            devices[device_name] = device

        configurations = parameters.get("configurations", None)
        return __cls__(
            devices=devices,
            name=name,
            configurations=configurations,
            config_file=filename,
        )

    def save_config(self, filename=None):
        raise NotImplementedError()
        return super().save_config(filename)

    def move_configuration_idx(self, idx: int, wait=False):
        for row in self.configurations:
            if row["idx"] == idx:
                self.current_config = row["value"]
                break
        else:
            raise ValueError(f"No configuration saved at index {idx}")
        for dev_name, value in self.current_config.items():
            # TODO async wait
            self.devices[dev_name].move_absolute(value, wait=wait)

    def move_configuration_name(self, name: str, wait=False):
        for row in self.configurations:
            if row["name"] == name:
                self.current_config = row["value"]
                break
        else:
            raise ValueError(f"No configuration saved with name '{name}'")
        for dev_name, value in self.current_config.items():
            # TODO async wait
            self.devices[dev_name].move_absolute(value, wait=wait)

    def update_keys(self, positions=None):
        if positions is None:
            positions = [dev.get_position() for dev in self.devices.values()]
        return self._update_keys(positions)

    def _update_keys(self, positions):
        pass

    def get_configuration(self, positions=None, tol=1e-1):
        if positions is not None:
            values = {k: p for k, p in zip(self.devices.keys(), positions)}
        else:
            values = {k: dev.get_position() for k, dev in self.devices.items()}
        for row in self.configurations:
            match = True
            for key, val in values.items():
                match = match and np.abs(row["value"][key] - val) <= tol
            if match:
                return row["idx"], row["name"]
        return None, "Unknown"
