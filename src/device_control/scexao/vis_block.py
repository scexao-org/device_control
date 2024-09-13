import os
import sys

from docopt import docopt
from swmain.redis import update_keys

from device_control.drivers import ThorlabsFlipMount


class VisBlock(ThorlabsFlipMount):
    CONF = "scexao/conf_vis_block.toml"
    PYRO_KEY = "VIS_BLOCK"
    format_str = "{0}: {1}"

    def _update_keys(self, position):
        _, state = self.get_configuration(position)
        update_keys(X_VISBLK=state.upper())

    def help_message(self):
        return """Usage:
    vis_block [-h | --help]
    vis_block status
    vis_block <pos>

Options:
    -h, --help   Show this screen
    <pos>        Move the mount 'in' or 'out'

Stage commands:
    status       Returns the current mount position"""


# setp 4. action
def main():
    vis_block = VisBlock.connect(os.getenv("WHICHCOMP") == "V")
    __doc__ = vis_block.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif args["status"]:
        posn, status = vis_block.get_status()
        print(status)
    elif args["<pos>"]:
        vis_block.move_configuration_name(args["<pos>"])
    vis_block.update_keys(posn)


if __name__ == "__main__":
    main()
