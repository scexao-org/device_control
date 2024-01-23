import os
import subprocess
import time

import astropy.units as u
import click
import usb.core
import usb.util
from scxconf.pyrokeys import VAMPIRES
from swmain.redis import update_keys

from device_control.base import ConfigurableDevice


class ArduinoError(RuntimeError):
    pass


class ArduinoTimeoutError(ArduinoError):
    pass


class VAMPIRESTrigger(ConfigurableDevice):
    CONF = "vampires/conf_vampires_trigger.toml"
    PYRO_KEY = VAMPIRES.TRIG

    def __init__(
        self,
        serial_kwargs=None,
        pulse_width: int = 10,  # us
        flc_offset: int = 20,  # us
        flc_enabled: bool = False,
        sweep_mode: bool = False,
        **kwargs,
    ):
        def_serial_kwargs = {"baudrate": 115200, "timeout": 0.5}
        def_serial_kwargs.update(serial_kwargs)
        super().__init__(serial_kwargs=def_serial_kwargs, **kwargs)
        self.reset_switch = VAMPIRESInlineUSBReset(serial="YKD6404")

        if isinstance(pulse_width, u.Quantity):
            self.pulse_width = int(pulse_width.to(u.us).value)
        if isinstance(flc_offset, u.Quantity):
            self.flc_offset = int(flc_offset.to(u.us).value)
        self.enabled = False
        self.pulse_width = int(pulse_width)
        self.flc_offset = int(flc_offset)
        self.flc_enabled = flc_enabled
        self.sweep_mode = sweep_mode

    def send_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())
            response = serial.readline()
            if len(response) == 0:
                msg = 'Arduino did not respond within timeout, which suggests it is locked up waiting for a "ready" response from the cameras. Try resetting the trigger.'
                raise ArduinoTimeoutError(msg)
            if response.strip() != b"OK":
                raise ArduinoError(response.decode().strip())

    def ask_command(self, command):
        with self.serial as serial:
            serial.write(f"{command}\n".encode())
            response = serial.readline().decode().strip()
            if len(response) == 0:
                msg = 'Arduino did not respond within timeout, which suggests it is locked up waiting for a "ready" response from the cameras. Try resetting the trigger.'
                raise ArduinoTimeoutError(msg)
            return response

    def get_jitter_half_width(self) -> int:
        return self.jitter_half_width

    def set_jitter_half_width(self, value):
        if isinstance(value, u.Quantity):
            self.jitter_half_width = int(self.jitter_half_width.to(u.us).value)
        else:
            self.jitter_half_width = int(value)
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
        self.update_keys()

    def disable_flc(self):
        self.flc_enabled = False
        self.set_parameters()
        self.update_keys()

    def get_parameters(self):
        response = self.ask_command(0)
        tokens = map(int, response.split())
        self.enabled = bool(next(tokens))
        self.pulse_width = next(tokens)
        self.flc_offset = next(tokens)
        self.jitter_half_width = next(tokens)
        trigger_mode = next(tokens)
        self.flc_enabled = bool(trigger_mode & 0x1)
        self.sweep_mode = bool(trigger_mode & 0x2)
        params = {
            "enabled": self.enabled,
            "pulse_width": self.pulse_width,
            "flc_offset": self.flc_offset,
            "jitter_half_width": self.jitter_half_width,
            "flc_enabled": self.flc_enabled,
            "sweep_mode": self.sweep_mode,
        }
        self.update_keys(params=params)
        return params

    def set_parameters(
        self,
        flc_enabled=None,
        flc_offset=None,
        pulse_width=None,
        jitter_half_width=None,
        sweep_mode=None,
    ):
        if flc_enabled is None:
            flc_enabled = self.flc_enabled
        if flc_offset is None:
            flc_offset = self.flc_offset
        if pulse_width is None:
            pulse_width = self.pulse_width
        if jitter_half_width is None:
            jitter_half_width = self.jitter_half_width
        if sweep_mode is None:
            sweep_mode = self.sweep_mode

        trigger_mode = int(flc_enabled) + (int(sweep_mode) << 1)
        cmd = f"1 {pulse_width:d} {flc_offset:d} {jitter_half_width:d} {trigger_mode:d}"
        self.send_command(cmd)
        params = dict(
            enabled=self.enabled,
            pulse_width=pulse_width,
            flc_offset=flc_offset,
            jitter_half_width=jitter_half_width,
            flc_enabled=flc_enabled,
        )
        self.update_keys(params=params)

    def disable(self):
        self.send_command(2)
        self.enabled = False
        self.update_keys(self.enabled)

    def enable(self):
        self.enabled = True
        self.update_keys(self.enabled)
        self.send_command(3)

    def reset(self):
        # toggle power using inline switch
        self.reset_switch.disable()
        time.sleep(0.1)
        self.reset_switch.enable()
        self.enabled = False
        update_keys(U_TRIGEN=str(False))

    def update_keys(self, enabled=None, params=None):
        if params is None:
            params = self.get_parameters()
        if enabled is None:
            enabled = params["enabled"]
        flc_enabled = params["flc_enabled"]
        flc_offset = params["flc_offset"]
        jitter_half_width = params["jitter_half_width"]
        pulse_width = params["pulse_width"]
        update_keys(
            U_TRIGEN=enabled,
            U_FLCEN=flc_enabled,
            U_TRIGJT=jitter_half_width,
            U_TRIGOF=flc_offset,
            U_TRIGPW=pulse_width,
        )

    def _config_extras(self):
        return {"delay": self.delay, "pulse_width": self.pulse_width, "flc_offset": self.flc_offset}

    def get_status(self):
        switch_status = self.reset_switch.status()
        if switch_status != "ON":
            return f"USB reset switch is {switch_status}"
        info = self.get_parameters()
        return info


class VAMPIRESInlineUSBReset:
    def __init__(self, serial=None):
        self.serial = serial
        self.outaddr = 0x1
        self.inaddr = 0x81
        self.bufsize = 64
        self.device = usb.core.find(idVendor=0x04D8, idProduct=0xF0CD)

    def __enter__(self):
        self._reattach = False
        if self.device.is_kernel_driver_active(0):
            self._reattach = True
            self.device.detach_kernel_driver(0)

        return self.device

    def __exit__(self, *args):
        usb.util.dispose_resources(self.device)
        if self._reattach:
            self.device.attach_kernel_driver(0)

    def send_command(self, command: int):
        with self as device:
            device.write(self.outaddr, chr(command))

    def ask_command(self, command: int):
        with self as device:
            device.write(self.outaddr, chr(command))
            reply = device.read(self.inaddr, self.bufsize)
        return reply

    def enable(self):
        subprocess.run([f"ykushcmd ykushxs -s {self.serial} -u"], shell=True, check=True)

        # subprocess.run(command, shell=True, check=True)
        # reply = self.ask_command(0x11)
        # assert reply[0] == 0x1

    def disable(self):
        subprocess.run([f"ykushcmd ykushxs -s {self.serial} -d"], shell=True, check=True)
        # reply = self.ask_command(0x01)
        # assert reply[0] == 0x1

    def status(self):
        result = subprocess.run(
            [f"ykushcmd ykushxs -s {self.serial} -g"], shell=True, capture_output=True
        )
        retval = result.stdout.decode().strip()
        if "ON" in retval:
            return "ON"
        elif "OFF" in retval:
            return "OFF"
        else:
            return "Unknown"
        # reply = self.ask_command(0x21)
        # assert reply[0] == 0x1
        # if reply[1] == 0x01:
        #     st = "OFF"
        # elif reply[1] == 0x11:
        #     st = "ON"
        # else:
        #     st = "UNKNOWN"
        # return st


@click.group("vampires_trigger", no_args_is_help=True)
@click.pass_context
def main(ctx):
    trigger = VAMPIRESTrigger.connect(local=os.getenv("WHICHCOMP", None) == "V")
    ctx.ensure_object(dict)
    ctx.obj["trigger"] = trigger


@main.command(help="Disable the external trigger")
@click.pass_obj
def disable(obj):
    obj["trigger"].disable()


@main.command(help="Enable the external trigger")
@click.pass_obj
def enable(obj):
    obj["trigger"].enable()


@main.command(
    short_help="Get the trigger status",
    help="Get the timing parameters and status of the external trigger",
)
@click.pass_obj
def status(obj):
    status = obj["trigger"].get_status()
    click.echo(status)


@main.command(help="Reset the external trigger")
@click.pass_obj
def reset(obj):
    obj["trigger"].reset()
    click.echo("trigger has been reset and is now disabled")


@main.command(
    "set",
    short_help="Set the trigger parameters",
    help="Set the external trigger parameters, which will automatically disable and enable the trigger if it is running.",
)
@click.option(
    "-f/-nf",
    "--flc/--no-flc",
    default=False,
    help="Enable/disable AFLC usage. Please limit AFLC usage to prevent ageing.",
)
@click.option(
    "-o", "--flc-offset", type=int, default=20, help="Use a custom FLC time delay, in us."
)
@click.option("-j", "--flc-jitter", type=int, default=50, help="FLC jitter half-width, in us.")
@click.option("-w", "--pulse-width", type=int, default=20, help="Use a custom pulse width, in us.")
@click.option(
    "--sweep-mode",
    default=False,
    type=bool,
    help="Enable sweep mode, which will increment the FLC offset by 1 us each loop (so two exposures).",
)
@click.pass_obj
def set_parameters(
    obj, flc: bool, flc_offset: int, pulse_width: int, flc_jitter: int, sweep_mode: bool
):
    trig_enabled = obj["trigger"].get_parameters()["enabled"]
    if trig_enabled:
        obj["trigger"].disable()
    obj["trigger"].set_parameters(
        flc_enabled=flc,
        flc_offset=flc_offset,
        jitter_half_width=flc_jitter,
        pulse_width=pulse_width,
        sweep_mode=sweep_mode,
    )


## Disabled currently because output from FLC controller fried arduino
# @main.command(
#     "check",
#     short_help="Check the FLC controller",
#     help="Send an FLC trigger pulse to see if controller is active",
# )
# @click.pass_obj
# def check(obj):
#     flc_good = obj["trigger"].flc_controller_enabled()
#     if flc_good:
#         click.echo("FLC controller is active")
#     else:
#         click.echo("FLC activity check failed!")
#         click.echo("FLC controller is not active")


if __name__ == "__main__":
    main()
