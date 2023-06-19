from logging import getLogger
from pathlib import Path

import numpy as np
import paramiko
import tomli
import tomli_w
from device_control import conf_dir
from serial import Serial

from swmain.network.pyroclient import connect

__all__ = ["ConfigurableDevice", "MotionDevice", "SSHDevice"]

# Interface for hardware devices- all subclasses must
# implement this!


class ConfigurableDevice:
    CONF = None
    PYRO_KEY = None

    def __init__(
        self,
        name=None,
        configurations=None,
        config_file=None,
        serial_kwargs=None,
        **kwargs,
    ):
        self.serial_kwargs = {"timeout": 0.5}
        self.serial_kwargs.update(serial_kwargs)
        self.serial = Serial(**self.serial_kwargs)
        self.configurations = configurations
        self.config_file = config_file
        self.name = name
        self.logger = getLogger(self.__class__.__name__)

    @classmethod
    def from_config(__cls__, filename, **kwargs):
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        parameters.update(kwargs)
        serial_kwargs = parameters.pop("serial", None)
        return __cls__(serial_kwargs=serial_kwargs, config_file=filename, **parameters)

    @classmethod
    def connect(__cls__, local=False, filename=None, pyro_key=None):
        if local:
            if filename is None:
                filename = conf_dir / __cls__.CONF
            return __cls__.from_config(filename)
        if pyro_key is None:
            pyro_key = __cls__.PYRO_KEY
        return connect(pyro_key)

    def save_config(self, filename=None):
        if filename is None:
            filename = self.config_file
        path = Path(filename)

        config = {
            "name": self.name,
            "configurations": self.configurations,
            "serial": self.serial_kwargs,
        }
        config.update(self._config_extras())
        with path.open("wb") as fh:
            tomli_w.dump(config, fh)
        self.logger.info(f"saved configuration to {path.absolute()}")

    def _config_extras(self):
        return {}

    def get_configurations(self):
        return self.configurations

    def set_configurations(self, value):
        self.configurations = value

    def get_name(self):
        return self.name

    def set_name(self, value: str):
        self.name = value


class MotionDevice(ConfigurableDevice):
    FORMAT_STR = "{0}: {1} {{{2}}}"

    def __init__(
        self,
        unit=None,
        offset=0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.unit = unit
        self.offset = offset

    def get_unit(self):
        return self.unit

    def set_unit(self, value):
        self.unit = value

    def get_offset(self):
        return self.offset

    def set_offset(self, value):
        self.offset = value

    def _config_extras(self):
        return {"unit": self.unit, "offset": self.offset}

    def get_position(self):
        pos = self._get_position() + self.offset
        self.update_keys(pos)
        return pos

    def _get_position(self):
        raise NotImplementedError()

    def get_target_position(self):
        pos = self._get_target_position() + self.offset
        return pos

    def _get_target_position(self):
        raise NotImplementedError()

    def home(self, wait=True):
        pos = self._home(wait=wait)
        self.update_keys(pos)
        return pos

    def _home(self, wait=True):
        raise NotImplementedError()

    def move_absolute(self, value, **kwargs):
        pos = self._move_absolute(value - self.offset, **kwargs)
        self.update_keys(pos)
        return pos

    def _move_absolute(self, value, wait=True):
        raise NotImplementedError()

    def move_relative(self, value, wait=True):
        pos = self._move_relative(value, wait=wait)
        self.update_keys(pos)
        return pos

    def _move_relative(self, value, wait=True):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def update_keys(self, position=None):
        if position is None:
            position = self.get_position()
        return self._update_keys(position)

    def _update_keys(self, position):
        pass

    def move_configuration(self, idx_or_name, **kwargs):
        if idx_or_name.isdigit():
            return self.move_configuration_idx(int(idx_or_name), **kwargs)

        return self.move_configuration_name(idx_or_name, **kwargs)

    def move_configuration_idx(self, idx: int, **kwargs):
        for row in self.configurations:
            if row["idx"] == idx:
                return self.move_absolute(row["value"], **kwargs)
        raise ValueError(f"No configuration saved at index {idx}")

    def move_configuration_name(self, name: str, **kwargs):
        for row in self.configurations:
            if row["name"].lower() == name.lower():
                return self.move_absolute(row["value"], **kwargs)
        raise ValueError(f"No configuration saved with name '{name}'")

    def get_configuration(self, position=None, tol=1e-1):
        if position is None:
            position = self.get_position()
        for row in self.configurations:
            if np.abs(position - row["value"]) <= tol:
                return row["idx"], row["name"]
        return None, "Unknown"

    def save_configuration(self, position=None, index=None, name=None, tol=1e-1, **kwargs):
        if position is None:
            position = self.get_position()
        current_config = self.get_configuration(position, tol=tol)
        if index is None:
            if current_config[0] is None:
                raise RuntimeError("Cannot save to an unknown configuration. Please provide index.")
            index = current_config[0]
            if name is None:
                name = current_config[1]

        # see if existing configuration
        for row in self.configurations:
            if row["idx"] == index:
                if name is not None:
                    row["name"] = name
                row["value"] = position
                self.logger.info(
                    f"updated configuration {index} '{row['name']}' to value {row['value']}"
                )
                break
        else:
            if name is None:
                raise ValueError("Must provide name for new configuration")
            self.configurations.append(dict(idx=index, name=name, value=position))
            self.logger.info(f"added new configuration {index} '{name}' with value {position}")

        # sort configurations dictionary in-place by index
        self.configurations.sort(key=lambda d: d["idx"])
        # save configurations to file
        self.save_config(**kwargs)
        self.update_keys()

    def get_status(self):
        posn = self.get_position()
        idx, name = self.get_configuration(posn)
        output = self.format_str.format(idx, name, posn)
        return posn, output


class SSHDevice:
    CONF = None
    PYRO_KEY = None

    def __init__(self, host, user=None, config_file=None):
        self.host = host
        self.user = user
        self._prepare_sshclient()
        self.config_file = config_file

    def _prepare_sshclient(self, **kwargs):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(self.host, username=self.user, **kwargs)

    def send_command(self, command: str):
        stdin, stdout, stderr = self.client.exec_command(command)

    def ask_command(self, command: str):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode()

    @classmethod
    def from_config(__cls__, filename, **kwargs):
        with open(filename, "rb") as fh:
            parameters = tomli.load(fh)
        parameters.update(kwargs)
        return __cls__(config_file=filename, **parameters.pop("ssh"), **parameters)

    @classmethod
    def connect(__cls__):
        filename = conf_dir / __cls__.CONF
        return __cls__.from_config(filename)
