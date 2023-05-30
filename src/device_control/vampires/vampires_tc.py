import sys

from docopt import docopt

from device_control.drivers import ThorlabsTC
from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (  # Requires scxconf and will fetch the IP addresses there.
    connect
)
from swmain.redis import update_keys


class VAMPIRESTC(ThorlabsTC):
    format_str = "{0:1d}: {1:8s}"

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
    vampires_tc <temp>
    vampires_tc (status|temp|enable|disable)

Options:
    -h, --help   Show this screen

Stage commands:
    <temp>       Sets the target temperature (in °C)
    temp         Returns the target temperature (in °C)
    status       Returns the temperature controller status
    enable       Enables the temperature controller PID loop
    disable      Disables the temperature controller PID loop"""


# setp 4. action
def main():
    vampires_tc = connect(PYRO_KEYS["tc"])
    __doc__ = vampires_tc.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    elif args["<temp>"].lower() in ("status", "st"):
        stat_dict = vampires_tc.status()
        enabled_str = "Enabled" if stat_dict["enabled"] else "Disabled"
        print(
            f"{enabled_str}: Tact = {vampires_tc.get_temp():4.01f}°C / Tset = {vampires_tc.get_target():4.01f}°C"
        )
    elif args["<temp>"].lower() in ("temp"):
        print(vampires_tc.get_temp())
    elif args["<temp>"].lower() in ("enable", "en"):
        vampires_tc.enable()
    elif args["<temp>"].lower() in ("disable", "dis"):
        vampires_tc.disable()
    elif args["<temp>"]:
        vampires_tc.set_target(float(args["<temp>"]))
    vampires_tc.update_keys()


if __name__ == "__main__":
    main()
