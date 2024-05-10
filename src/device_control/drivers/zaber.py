from zaber_motion import Library, Units
from zaber_motion.binary import BinarySettings, CommandCode, Connection, Device
import fcntl

from device_control.base import MotionDevice

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
    def __init__(self, delay=0.1, **kwargs):
        self.device_number = kwargs["serial_kwargs"].pop("device_number")
        super().__init__(**kwargs)
        del self.serial
        self.serial = None
        self.zab_unit = ZABER_UNITS[self.unit]
        self.delay = delay

    def get_serial_kwargs(self):
        return {**self.serial_kwargs, "device_number": self.device_number}

    def __enter__(self) -> Device:
        self._lockfile = open(self.flockpath, 'r')
        fcntl.flock(self._lockfile.fileno(), fcntl.LOCK_EX)

        self.connection = Connection.open_serial_port(self.serial_kwargs["port"])
        device = self.connection.get_device(self.device_number)
        device.identify()
        return device

    def __exit__(self, *args):
        self.connection.close()
        fcntl.flock(self._lockfile.fileno(), fcntl.LOCK_UN)
        self._lockfile.close()

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

    def _move_absolute(self, value):
        with self as device:
            posn = device.move_absolute(value, self.zab_unit)
            self.update_keys(posn)

    def _move_relative(self, value):
        with self as device:
            posn = device.move_relative(value, self.zab_unit)
            self.update_keys(posn)

    def reset(self):
        self.send_command(0)

    def _home(self):
        with self as device:
            posn = device.home()
            self.update_keys(posn)

    def stop(self):
        with self as device:
            device.stop()
        self.update_keys()
