import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VAMPIRES

from device_control.drivers import ThorlabsTC
from swmain.redis import update_keys


class VAMPIRESTC(ThorlabsTC):
    CONF = "vampires/conf_vampires_tc.toml"
    PYRO_KEY = VAMPIRES.TC
    format_str = "{0:s}: Tact = {1:4.01f}°C / {2:4.01f}°C"

    def update_keys(self, temperature=None):
        if temperature is None:
            temperature = self.get_temp()
        update_keys(U_FLCTMP=temperature)

    def help_message(self):
        return f"""Usage:
    vampires_tc [-h | --help]
    vampires_tc (status|temp|enable|disable)
    vampires_tc <setpoint>

Options:
    -h, --help   Show this screen
    <temp>       Sets the target temperature (in °C)

Stage commands:
    temp         Returns the target temperature (in °C)
    status       Returns the temperature controller status
    enable       Enables the temperature controller PID loop
    disable      Disables the temperature controller PID loop"""


# setp 4. action
def main():
    vampires_tc = VAMPIRESTC.connect(local=os.getenv("WHICHCOMP") == "V")
    __doc__ = vampires_tc.help_message()
    args = docopt(__doc__, options_first=True)
    temperature = None
    if len(sys.argv) == 1:
        print(__doc__)
    elif args["status"]:
        temperature, status = vampires_tc.get_status()
        print(status)
    elif args["temp"]:
        print(vampires_tc.get_temp())
    elif args["enable"]:
        vampires_tc.enable()
    elif args["disable"]:
        vampires_tc.disable()
    elif args["<setpoint>"]:
        vampires_tc.set_target(float(args["<setpoint>"]))
    vampires_tc.update_keys(temperature)


if __name__ == "__main__":
    main()
