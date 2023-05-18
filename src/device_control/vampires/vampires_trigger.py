import astropy.units as u
import tomli
from serial import Serial

# from swmain.redis import update_keys
from device_control.base import ConfigurableDevice


class VAMPIRESTrigger(ConfigurableDevice):
    def __init__(
        self,
        serial_kwargs,
        tint: int = 2000,  # us
        pulse_width: int = 10,  # us
        flc_offset: int = 20,  # us
        flc_enabled: bool = True,
        sweep_mode: bool = False,
        **kwargs,
    ):
        serial_kwargs = dict(
            {"baudrate": 115200, "write_timeout": 0.5}, **serial_kwargs
        )
        super().__init__(self, serial_kwargs=serial_kwargs, **kwargs)

        if isinstance(tint, u.Quantity):
            self.tint = int(tint.to(u.us).value)
        if isinstance(pulse_width, u.Quantity):
            self.pulse_width = int(pulse_width.to(u.us).value)
        if isinstance(flc_offset, u.Quantity):
            self.flc_offset = int(flc_offset.to(u.us).value)

        self.flc_enabled = flc_enabled
        self.sweep_mode = sweep_mode

    def send_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())

    def ask_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())
            return serial.readline()

    def get_tint(self) -> int:
        return self.tint

    def set_tint(self, value):
        if isinstance(value, u.Quantity):
            self.tint = int(self.tint.to(u.us).value)
        else:
            self.tint = int(value)
        self.set_parameters()

    def get_pulse_width(self) -> int:
        return self.pulse_width

    def set_pulse_width(self, value):
        if isinstance(value, u.Quantity):
            self.pulse_width = int(self.pulse_width.to(u.us).value)
        else:
            self.pulse_width = int(value)
        self.set_parameters()

    def get_flc_offset(self) -> int:
        return self.flc_offset

    def set_flc_offset(self, value):
        if isinstance(value, u.Quantity):
            self.flc_offset = int(self.flc_offset.to(u.us).value)
        else:
            self.flc_offset = int(value)
        self.set_parameters()

    def is_flc_enabled(self) -> bool:
        return self.flc_enabled

    def enable_flc(self):
        self.flc_enabled = True
        self.set_parameters()

    def get_parameters(self):
        response = self.ask_command(0)
        tokens = response.split()
        enabled = bool(tokens[0])
        self.tint = int(tokens[1])
        self.pulse_width = int(tokens[2])
        self.flc_offset = int(tokens[3])
        trigger_mode = int(tokens[4])
        self.flc_enabled = trigger_mode & 0x1
        self.sweep_mode = trigger_mode & 0x2
        # self.update_keys()
        return {
            "enabled": enabled,
            "integration_time": self.tint,
            "pulse_width": self.pulse_width,
            "flc_offset": self.flc_offset,
            "flc_enabled": self.flc_enabled,
            "sweep_mode": self.sweep_mode,
        }

    def set_parameters(self):
        trigger_mode = int(self.flc_enabled) + (int(self.sweep_mode) << 1)
        cmd = "1 {:d} {:d} {:d} {:d}".format(
            self.tint, self.pulse_width, self.flc_offset, trigger_mode
        )
        response = self.ask_command(cmd)
        if response != "OK":
            raise ValueError(response)
        # self.update_keys()

    def set_tint(self, tint):
        self.tint = tint
        self.set_parameters()

    def disable(self):
        self.send_command(2)

    def enable(self):
        self.send_command(3)

    # def update_keys(self):
    #     update_keys(
    #         U_FLCEN="ON" if self.flc_enabled else "OFF",
    #         U_FLCOFF=self.flc_offset,
    #         U_TRIGPW=self.pulse_width
    #     )
    def _extra_config(self):
        return {
            "pulse_width": self.pulse_width,
            "flc_offset": self.flc_offset,
        }

    def status(self):
        info = self.get_timing_info()
        # self.update_keys()
        return info
