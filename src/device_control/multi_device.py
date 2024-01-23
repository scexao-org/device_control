from pathlib import Path

import numpy as np
import tomli
import tomli_w

from device_control.base import ConfigurableDevice
from device_control.drivers.conex import CONEXDevice
from device_control.drivers.zaber import ZaberDevice

__all__ = ["MultiDevice"]


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

    def home(self, name, **kwargs):
        result = self.devices[name].home(**kwargs)
        self.update_keys()
        return result

    def move_absolute(self, name, value, **kwargs):
        result = self.devices[name].move_absolute(value, **kwargs)
        self.update_keys()
        return result

    def move_relative(self, name, value, **kwargs):
        result = self.devices[name].move_relative(value, **kwargs)
        self.update_keys()
        return result

    def stop(self, name=None):
        if name is None:
            for device in self.devices.values():
                device.stop()
        else:
            self.devices[name].stop()
        self.update_keys()

    @classmethod
    def from_config(__cls__, filename):
        with Path.open(filename, "rb") as fh:
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
                msg = f"motion stage type not recognized: {device_config['type']}"
                raise ValueError(msg)
            devices[device_name] = device

        configurations = parameters.get("configurations", None)
        return __cls__(
            devices=devices, name=name, configurations=configurations, config_file=filename
        )

    def save_config(self, filename=None):
        if filename is None:
            filename = self.config_file
        path = Path(filename)

        config = {"name": self.name, "configurations": self.configurations}
        config.update(self._config_extras())
        config["devices"] = []
        for key, device in self.devices.items():
            if isinstance(device, CONEXDevice):
                type = "conex"
            elif isinstance(device, ZaberDevice):
                type = "zaber"
            devconf = {"name": key, "type": type, "serial": device.get_serial_kwargs()}
            devconf.update(device._config_extras())
            config["devices"].append(devconf)
        with path.open("wb") as fh:
            tomli_w.dump(config, fh)
        self.logger.info(f"saved configuration to {path.absolute()}")

    def _config_extras(self):
        return {}

    def save_configuration(self, positions=None, index=None, name=None, tol=1e-1, **kwargs):
        if positions is None:
            dev_posns = {k: dev.get_position() for k, dev in self.devices.items()}
        else:
            dev_posns = {k: pos for k, pos in zip(self.devices.keys(), positions)}

        current_config = self.get_configuration(positions=dev_posns.values(), tol=tol)
        if index is None:
            if current_config[0] is None:
                msg = "Cannot save to an unknown configuration. Please provide index."
                raise RuntimeError(msg)
            index = current_config[0]
            if name is None:
                name = current_config[1]

        # see if existing configuration
        for row in self.configurations:
            if row["idx"] == index:
                if name is not None:
                    row["name"] = name
                row["value"] = dev_posns
                self.logger.info(
                    f"updated configuration {index} '{row['name']}' to value {row['value']}"
                )
                break
        else:
            if name is None:
                msg = "Must provide name for new configuration"
                raise ValueError(msg)
            self.configurations.append(dict(idx=index, name=name, values=dev_posns.values()))
            self.logger.info(
                f"added new configuration {index} '{name}' with values {dev_posns.values()}"
            )

        # sort configurations dictionary in-place by index
        self.configurations.sort(key=lambda d: d["idx"])
        # save configurations to file
        self.save_config(**kwargs)
        self.update_keys()

    def move_configuration(self, idx_or_name, **kwargs):
        if isinstance(idx_or_name, int) or idx_or_name.isdigit():
            return self.move_configuration_idx(int(idx_or_name), **kwargs)

        return self.move_configuration_name(idx_or_name, **kwargs)

    def move_configuration_idx(self, idx: int):
        for row in self.configurations:
            if row["idx"] == idx:
                self.current_config = row["value"]
                break
        else:
            msg = f"No configuration saved at index {idx}"
            raise ValueError(msg)
        for dev_name, value in self.current_config.items():
            # TODO async wait
            self.devices[dev_name].move_absolute(value)
            self.update_keys()

    def move_configuration_name(self, name: str):
        for row in self.configurations:
            if row["name"].lower() == name.lower():
                self.current_config = row["value"]
                break
        else:
            msg = f"No configuration saved with name '{name}'"
            raise ValueError(msg)
        for dev_name, value in self.current_config.items():
            self.devices[dev_name].move_absolute(value)
            self.update_keys()

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

    def get_status(self):
        posns = [dev.get_position() for dev in self.devices.values()]
        idx, name = self.get_configuration(posns)
        output = self.format_str.format(idx, name, *posns)
        return posns, output
