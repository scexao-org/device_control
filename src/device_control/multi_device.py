from typing import Union

import numpy as np
import tomli
import tomli_w
from pathlib import Path

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
        if filename is None:
            filename = self.config_file
        path = Path(filename)

        config = {
            "name": self.name,
            "configurations": self.configurations,
        }
        config.update(self._config_extras())
        config["devices"] = []
        for key, device in self.devices.items():
            if isinstance(device, CONEXDevice):
                type = "conex"
            elif isinstance(device, ZaberDevice):
                type = "zaber"
            devconf = {"name": key, "type": type, "serial": device.serial_kwargs}
            devconf.update(device._config_extras())
            config["devices"].append(devconf)
        with path.open("wb") as fh:
            tomli_w.dump(config, fh)
        self.logger.info(f"saved configuration to {path.absolute()}")

    def _config_extras(self):
        return {}

    def save_configuration(
        self, positions=None, index=None, name=None, tol=1e-1, **kwargs
    ):
        if positions is None:
            values = {k: dev.get_position() for k, dev, in self.devices.items()}
        else:
            values = {k: pos for k, pos in zip(self.devices.keys(), positions)}

        current_config = self.get_configuration(positions=values.values(), tol=tol)
        if index is None:
            if current_config[0] is None:
                raise RuntimeError(
                    "Cannot save to an unknown configuration. Please provide index."
                )
            index = current_config[0]
            if name is None:
                name = current_config[1]

        # see if existing configuration
        for row in self.configurations:
            if row["idx"] == index:
                if name is not None:
                    row["name"] = name
                row["value"] = values
                self.logger.info(
                    f"updated configuration {index} '{row['name']}' to value {row['value']}"
                )
                break
        else:
            if name is None:
                raise ValueError("Must provide name for new configuration")
            self.configurations.append(dict(idx=index, name=name, values=values))
            self.logger.info(
                f"added new configuration {index} '{name}' with value {values}"
            )

        # sort configurations dictionary in-place by index
        self.configurations.sort(key=lambda d: d["idx"])
        # save configurations to file
        return self.save_config(**kwargs)

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
