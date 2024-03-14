import os
import sys
import time

from docopt import docopt
from scxconf.pyrokeys import VISWFS

from device_control.drivers.thorlabs import ThorlabsElliptec
from swmain.redis import update_keys


class VISWFSHWP(ThorlabsElliptec):
    CONF = "viswfs/conf_viswfs_hwp.toml"
    PYRO_KEY = VISWFS.HWP
    format_str = "{0}: {1}"

    def _update_keys(self, position):
        _, state = self.get_configuration(position)
        update_keys(U_HWPST=state.upper())

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    viswfs_hwp [-h | --help]
    viswfs_hwp (status|home|goto|nudge) [<pos>]
    viswfs_hwp <configuration>

Options:
    -h, --help   Show this screen

Stage commands:
    status       Returns the current mount position  

Configurations:
{configurations}"""



# setp 4. action
def main():
    viswfs_hwp = VISWFSHWP.connect(os.getenv("WHICHCOMP"))
    __doc__ = viswfs_hwp.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif args["status"]:
        posn, status = viswfs_hwp.get_status()
        print(status)
    elif args["home"]:
        viswfs_hwp.home()
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        viswfs_hwp.set_position(new_pos)
    elif args["nudge"]:
        new_pos = float(args["<pos>"])
        viswfs_hwp.move_relative(new_pos)
    elif args["<configuration>"]:
        viswfs_hwp.move_configuration(args["<configuration>"])
        time.sleep(0.1)
    viswfs_hwp.update_keys(posn)


if __name__ == "__main__":
    main()
