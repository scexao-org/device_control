import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VISWFS
<<<<<<< HEAD
from swmain.redis import update_keys

from device_control.drivers import ZaberDevice
=======

from device_control.drivers import ZaberDevice
from swmain.redis import update_keys
>>>>>>> adding device control for nlCWFS


class VISWFSTrombone2(ZaberDevice):
    CONF = "viswfs/conf_viswfs_trombone2.toml"
    PYRO_KEY = VISWFS.TROMBONE2
    format_str = "{0}: {1:10s} {{{2:5.02f} mm}}"

    def _update_keys(self, position):
        _, name = self.get_configuration(position=position)
        update_keys(U_TB2=name, U_TB2CF=position)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    viswfs_trombone2 [-h | --help]
    viswfs_trombone2 (status|position|home|goto|nudge|stop|reset) [<pos>]
    viswfs_trombone2 <configuration>

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
    viswfs_trombone2 = VISWFSTrombone2.connect(os.getenv("WHICHCOMP"))
    __doc__ = viswfs_trombone2.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        posn, status = viswfs_trombone2.get_status()
        print(status)
    elif args["position"]:
        posn = viswfs_trombone2.get_position()
        print(posn)
    elif args["home"]:
        viswfs_trombone2.home()
    elif args["goto"]:
        new_pos = float(args["<pos>"])
<<<<<<< HEAD
        if new_pos > 50:
=======
        if new_pos > 45:
>>>>>>> adding device control for nlCWFS
            print("Limitted!!!!")
        else:
            viswfs_trombone2.move_absolute(new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        posn = viswfs_trombone2.get_position() + rel_pos
<<<<<<< HEAD
        if posn > 50:
=======
        if posn > 45:
>>>>>>> adding device control for nlCWFS
            print("Limitted!!!!")
        else:
            viswfs_trombone2.move_relative(rel_pos)
    elif args["stop"]:
        viswfs_trombone2.stop()
    elif args["reset"]:
        viswfs_trombone2.reset()
    elif args["<configuration>"]:
        viswfs_trombone2.move_configuration(args["<configuration>"])
    viswfs_trombone2.update_keys(posn)


if __name__ == "__main__":
    main()
