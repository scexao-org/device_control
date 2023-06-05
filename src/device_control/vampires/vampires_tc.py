import sys
import os

from docopt import docopt

from device_control.pyro_keys import VAMPIRES
from device_control.drivers import ThorlabsTC
from swmain.redis import update_keys


class VAMPIRESTC(ThorlabsTC):
    CONF = "vampires/conf_vampires_tc.toml"
    PYRO_KEY = VAMPIRES.TC
    format_str = "{0:s}: Tact = {1:4.01f}°C / {2:4.01f}°C Taux = {3:4.01f}°C"

    def update_keys(self, temperatures=None):
        if temperatures is None:
            flc_temp = self.get_temp()
            aux_temp = self.get_aux_temp()
        else:
            flc_temp, aux_temp = temperatures
        update_keys(U_BENTMP=aux_temp, U_FLCTMP=flc_temp)

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
    temps = None
    if len(sys.argv) == 1:
        print(__doc__)
    elif args["status"]:
        stat_dict = vampires_tc.status()
        enabled_str = "Enabled" if stat_dict["enabled"] else "Disabled"
        flc_temp = vampires_tc.get_temp()
        targ_temp = vampires_tc.get_target()
        aux_temp = vampires_tc.get_aux_temp()
        print(vampires_tc.format_str.format(enabled_str, flc_temp, targ_temp, aux_temp))
    elif args["temp"]:
        print(vampires_tc.get_temp())
    elif args["enable"]:
        vampires_tc.enable()
    elif args["disable"]:
        vampires_tc.disable()
    elif args["<setpoint>"]:
        vampires_tc.set_target(float(args["<setpoint>"]))
    vampires_tc.update_keys(temps)


if __name__ == "__main__":
    main()
