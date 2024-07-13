import abc
from dataclasses import dataclass, field
from numbers import Number
from pathlib import Path
from typing import Any, ClassVar, Literal, Optional

import paramiko
import serial
import tomli
from loguru import logger
from swmain import redis
from swmain.network.pyroclient import connect


@dataclass
class DeviceDriver(abc.ABC):
    name: str

    def get_name(self):
        return self.name

    def set_name(self, name: str):
        self.name = name

    @abc.abstractmethod
    @classmethod
    def from_dict(__cls__, config: dict[str, Any]):
        """Create this device from a dictionary"""

    @abc.abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary with this device's configuration"""


@dataclass
class SerialDriver(DeviceDriver):
    address: str
    serial_kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.serial = serial.Serial(self.address, **self.serial_kwargs)

    @classmethod
    def from_dict(__cls__, config: dict[str, Any]):
        name = config.pop("name")
        address = config.pop("address")
        return __cls__(name=name, address=address, serial_kwargs=config)

    def to_dict(self):
        config_dict = dict(address=self.address, **self.serial_kwargs)
        return config_dict

    @abc.abstractmethod
    def send(self, command: str):
        """Send a command to the serial device with appropriate logging and checking"""

    @abc.abstractmethod
    def ask(self, command: str):
        """Send a command with a reply to the serial device with appropriate logging and checking"""


@dataclass
class SSHDriver(DeviceDriver):
    host: str
    user: str
    ssh_kwargs: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.load_system_host_keys()
        self.ssh_client.connect(self.host, username=self.user, **self.ssh_kwargs)

    @classmethod
    def from_dict(__cls__, config: dict[str, Any]):
        name = config.pop("name")
        host = config.pop("host")
        user = config.pop("user")
        return __cls__(name=name, host=host, user=user, ssh_kwargs=config)

    def to_dict(self):
        config_dict = dict(host=self.host, user=self.user, **self.ssh_kwargs)
        return config_dict

    def send(self, command: str):
        logger.debug(f"SSH command | {self.name} | {self.command}")
        stdin, stdout, stderr = self.client.exec_command(command)
        logger.debug(f"SSH reply | {self.name} | {stdout.read().decode()}")

    def ask(self, command: str):
        logger.debug(f"SSH command | {self.name} | {self.command}")
        stdin, stdout, stderr = self.client.exec_command(command)
        reply = stdout.read().decode()
        logger.debug(f"SSH reply | {self.name} | {reply}")
        return reply


@dataclass
class MotionDriver(DeviceDriver, abc.ABC):
    unit: str
    offset: Number = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_unit(self):
        return self.unit

    def set_unit(self, value: str):
        self.unit = value

    def get_offset(self):
        return self.offset

    def set_offset(self, value: Number):
        self.offset = value

    def get_position(self):
        """Return position (with offsets) and update keywords"""
        pos = self._get_position() + self.offset
        self.update_keys(pos)
        return pos

    def get_target_position(self):
        """Return target position (with offsets) and update keywords"""
        pos = self._get_target_position() + self.offset
        return pos

    def home(self):
        """Home device and update keywords"""
        pos = self._home()
        self.update_keys(pos)
        return pos

    def move_absolute(self, value, **kwargs):
        """Move device to absolute position (including offsets) and update keywords"""
        pos = self._move_absolute(value - self.offset, **kwargs)
        self.update_keys(pos)
        return pos

    def move_relative(self, value):
        """Move device by relative value and update keywords"""
        pos = self._move_relative(value)
        self.update_keys(pos)
        return pos

    def stop(self):
        """Stop all motion from device"""
        self._stop()
        self.update_keys()

    # abstract methods
    @abc.abstractmethod
    def _get_position(self):
        """Device-specific method for getting the current position"""

    @abc.abstractmethod
    def _get_target_position(self):
        """Device-specific method for getting the target position"""

    @abc.abstractmethod
    def _home(self):
        """Device-specific method for homing"""

    @abc.abstractmethod
    def _move_absolute(self, value):
        """Device-specific method for moving to absolute position"""

    @abc.abstractmethod
    def _move_relative(self, value):
        """Device-specific method for moving by relative position"""

    @abc.abstractmethod
    def _stop(self):
        """Device-specific method for stopping"""


##################################################################################


class PyroMixin:
    pyro_key: ClassVar[str]

    def connect_pyro(self):
        return connect(self.pyro_key)


class RedisMixin:
    def update_redis(self, params: dict[str, Any]):
        """Update the scexao redis"""
        redis.update_keys(**params)

    def update_status(self, params: dict[str, Any]):
        super().update_status(params)
        self.update_redis(params)


@dataclass
class Configuration:
    index: int
    name: str
    values: dict[str, str | Number]


##################################################################################


@dataclass
class ConfigurableDevice(abc.ABC):
    name: str
    conf_path: Path
    drivers: dict[str, DeviceDriver] = field(default_factory=dict)
    computer: Optional[Literal["scexao2", "scexaoV"]] = None

    @classmethod
    def from_dict(__cls__, config_dict, **kwargs):
        name = config_dict.pop("name", "")
        drivers = {}
        for device in config_dict.pop("devices", []):
            driver_type = device.pop("driver")
            if driver_type == "serial":
                driver = SerialDriver.from_dict(device)
            elif driver_type == "ssh":
                driver = SSHDriver.from_dict(device)
            else:
                msg = f"Did not recognize device driver type {driver!r}"
                raise ValueError(msg)
            drivers[driver.name] = driver

        configurations = []
        for config in config_dict.pop("configurations", []):
            configurations.append(Configuration(**config))
        sorted_configurations = list(sorted(configurations, key=lambda c: c.index))
        kwds = {**config_dict, **kwargs}
        return __cls__(name=name, drivers=drivers, configs=sorted_configurations, **kwds)

    @abc.abstractmethod
    def to_dict(self):
        pass

    @classmethod
    def from_config(__cls__, filename, **kwargs):
        path = Path(filename)
        with path.open("rb") as fh:
            config = tomli.load(fh)
        return __cls__.from_dict(config, conf_path=path, **kwargs)

    @abc.abstractmethod
    def update_status(self, params: dict[str, Any]):
        """Update any relevant status, including mixins"""
