from docopt import docopt
import os
import sys

from swmain.network.pyroclient import connect # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

vampires_camfocus = connect(PYRO_KEYS["camfocus"])

__doc__ = f"""Usage:
    vampires_camfocus [-h | --help]
    vampires_camfocus [-w | --wait] (status|target|home|goto|nudge|stop|reset) [<pos>]

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
    status          Returns the current position of the focus stage, in mm
    target          Returns the target position of the focus stage, in mm
    home            Homes the focus stage
    goto  <pos>     Move the focus stage to the given position, in mm
    nudge <pos>     Move the focus stage relatively by the given position, in mm
    stop            Stop the focus stage
    reset           Reset the focus stage"""

# setp 4. action
def main():
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        print(vampires_camfocus.position)
    elif args["target"]:
        print(vampires_camfocus.target_position)
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

if __name__ == "__main__":
    main()