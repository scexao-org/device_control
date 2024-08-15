import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VISWFS
from swmain.redis import update_keys

from device_control.drivers import ZaberDevice


class VISWFSCamFocus(ZaberDevice):
    CONF = "viswfs/conf_viswfs_camfocus.toml"
    PYRO_KEY = VISWFS.CAMFCS
    format_str = "{0}: {1:10s} {{{2:5.02f} mm}}"

    def _update_keys(self, position):
        _, name = self.get_configuration(position=position)
        update_keys(U_CAMFCS=name, U_CAMFCF=position)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    viswfs_camfocus [-h | --help]
    viswfs_camfocus (status|position|home|goto|nudge|stop|reset) [<pos>]
    viswfs_camfocus <configuration>

Options:
    -h, --help   Show this screen

Wheel commands:
    status          Returns the current status of the focus stage
    position        Returns the current position of the focus stage, in mm
    home            Homes the focus stage
    goto  <pos>     Move the focus stage to the given position, in mm
    nudge <pos>     Move the focus stage relatively by the given position, in mm
    stop            Stop the focus stage
    reset           Reset the focus stage  

Configurations:
{configurations}"""


# setp 4. action
def main():
    viswfs_camfocus = VISWFSCamFocus.connect(os.getenv("WHICHCOMP", "") == "AORTS")
    __doc__ = viswfs_camfocus.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        posn, status = viswfs_camfocus.get_status()
        print(status)
    elif args["position"]:
        posn = viswfs_camfocus.get_position()
        print(posn)
    elif args["home"]:
        viswfs_camfocus.home()
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        viswfs_camfocus.move_absolute(new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        viswfs_camfocus.move_relative(rel_pos)
    elif args["stop"]:
        viswfs_camfocus.stop()
    elif args["reset"]:
        viswfs_camfocus.reset()
    elif args["<configuration>"]:
        viswfs_camfocus.move_configuration(args["<configuration>"])
    viswfs_camfocus.update_keys(posn)


if __name__ == "__main__":
    main()
