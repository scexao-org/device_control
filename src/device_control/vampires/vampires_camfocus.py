import os
import sys

from docopt import docopt

from device_control.drivers import ZaberDevice
from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from swmain.redis import update_keys


class VAMPIRESCamFocus(ZaberDevice):
    format_str = "{0:4.02f} mm"

    def _update_keys(self, position):
        _, name = self.get_configuration(position=position)
        update_keys(U_CAMFCS=name.upper(), U_CAMFCF=position)

    def help_message(self):
        return f"""Usage:
    vampires_camfocus [-h | --help]
    vampires_camfocus [-w | --wait] (status|position|home|goto|nudge|stop|reset) [<pos>]

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Wheel commands:
    status          Returns the current status of the focus stage
    position        Returns the current position of the focus stage, in mm
    home            Homes the focus stage
    goto  <pos>     Move the focus stage to the given position, in mm
    nudge <pos>     Move the focus stage relatively by the given position, in mm
    stop            Stop the focus stage
    reset           Reset the focus stage"""


# setp 4. action
def main():
    vampires_camfocus = connect(PYRO_KEYS["camfocus"])
    __doc__ = vampires_camfocus.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        print(VAMPIRESCamFocus.format_str.format(vampires_camfocus.get_position()))
    elif args["position"]:
        print(vampires_camfocus.get_position())
    elif args["home"]:
        vampires_camfocus.home(wait=args["--wait"])
    elif args["goto"]:
        pos = float(args["<pos>"])
        vampires_camfocus.move_absolute(pos, wait=args["--wait"])
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_camfocus.move_relative(rel_pos, wait=args["--wait"])
    elif args["stop"]:
        vampires_camfocus.stop()
    elif args["reset"]:
        vampires_camfocus.reset()
    vampires_camfocus.update_keys()


if __name__ == "__main__":
    main()