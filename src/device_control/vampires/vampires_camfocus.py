import os
import sys

from docopt import docopt

from device_control.drivers import ZaberDevice
from device_control.pyro_keys import VAMPIRES
from swmain.redis import update_keys


class VAMPIRESCamFocus(ZaberDevice):
    CONF = "vampires/conf_vampires_camfocus.toml"
    PYRO_KEY = VAMPIRES.CAMFCS
    format_str = "{0:4.02f} mm"

    def _update_keys(self, position):
        _, name = self.get_configuration(position=position)
        update_keys(U_CAMFCS=name.upper(), U_CAMFCF=position)

    def help_message(self):
        return f"""Usage:
    vampires_camfocus [-h | --help]
    vampires_camfocus (status|position|home|goto|nudge|stop|reset) [<pos>]

Options:
    -h, --help   Show this screen

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
    vampires_camfocus = VAMPIRESCamFocus.connect(os.getenv("WHICHCOMP") == "V")
    __doc__ = vampires_camfocus.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        posn = vampires_camfocus.get_position()
        print(vampires_camfocus.format_str.format(posn))
    elif args["position"]:
        posn = vampires_camfocus.get_position()
        print(posn)
    elif args["home"]:
        vampires_camfocus.home()
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        vampires_camfocus.move_absolute(new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_camfocus.move_relative(rel_pos)
    elif args["stop"]:
        vampires_camfocus.stop()
    elif args["reset"]:
        vampires_camfocus.reset()
    vampires_camfocus.update_keys(posn)


if __name__ == "__main__":
    main()
