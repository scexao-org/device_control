import logging

from zaber_motion import Library, Units
from zaber_motion.binary import BinarySettings, CommandCode, Connection

from ..base import MotionDevice

__all__ = ["ZaberDevice"]

ZABER_UNITS = {
    "step": Units.NATIVE,
    "mm": Units.LENGTH_MILLIMETRES,
    "cm": Units.LENGTH_CENTIMETRES,
    "um": Units.LENGTH_MICROMETRES,
    "in": Units.LENGTH_INCHES,
    "deg": Units.ANGLE_DEGREES,
    "rad": Units.ANGLE_RADIANS,
}

Library.enable_device_db_store()


class ZaberDevice(MotionDevice):
    def __init__(self, device_address=1, delay=0.1, **kwargs):
        super().__init__(**kwargs)
        self.device_address = device_address
        self.zab_unit = ZABER_UNITS[self.unit]
        self.delay = delay

    def _config_extras(self):
        extras = super()._config_extras()
        extras["device_address"] = self.device_address
        return extras

    def __enter__(self):
        self.connection = Connection.open_serial_port(self.serial_kwargs["port"])
        device = self.connection.get_device(self.device_address)
        device.identify()
        return device

    def __exit__(self, *args):
        self.connection.close()

    def _get_position(self):
        with self as dev:
            return dev.get_position(self.zab_unit)

    def _get_target_position(self):
        return self._position

    def send_command(self, index: int, values=0):
        with self as device:
            message = device.generic_command(CommandCode(index), values)
        return message.data

    def get_setting(self, index: int):
        with self as device:
            retval = device.settings.get(BinarySettings(index))
        return retval

    def _move_absolute(self, value, wait=False):
        with self as device:
            device.move_absolute(value, self.zab_unit)
            if wait:
                device.wait_until_idle()

    def move_relative(self, value, wait=False):
        with self as device:
            device.move_relative(value, self.zab_unit)
            if wait:
                device.wait_until_idle()

    def reset(self):
        self.send_command(0)

    def home(self, wait=False):
        with self as device:
            device.home()
            if wait:
                device.wait_until_idle()

    def stop(self):
        with self as device:
            return device.stop()
