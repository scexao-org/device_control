import os
import sys
import time

from docopt import docopt
from scxconf.pyrokeys import VISWFS
from swmain.redis import update_keys

from device_control.drivers import ThorlabsFlipMount


class VISWFSFlipMount2(ThorlabsFlipMount):
    CONF = "viswfs/conf_viswfs_flipmount2.toml"
    PYRO_KEY = VISWFS.FLIPMOUNT2
    format_str = "{0}: {1}"

    def _update_keys(self, position):
        _, state = self.get_configuration(position)
        update_keys(U_FM2ST=state.upper())

    def help_message(self):
        return """Usage:
    viswfs_flipmount2 [-h | --help]
    viswfs_flipmount2 status
    viswfs_flipmount2 <pos>

Options:
    -h, --help   Show this screen
    <pos>        Move the mount 'in' or 'out'

Stage commands:
    status       Returns the current mount position"""


# setp 4. action
def main():
    viswfs_flip = VISWFSFlipMount2.connect(os.getenv("WHICHCOMP"))
    __doc__ = viswfs_flip.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif args["status"]:
        posn, status = viswfs_flip.get_status()
        print(status)
    elif args["<pos>"]:
        viswfs_flip.move_configuration_name(args["<pos>"])
        time.sleep(0.1)
    viswfs_flip.update_keys(posn)


if __name__ == "__main__":
    main()
