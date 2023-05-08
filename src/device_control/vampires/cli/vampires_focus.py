from docopt import docopt
import os
import sys

from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

vampires_focus = connect(PYRO_KEYS["focus"])

format_str = "{0}: {1:10s} {{{2:5.02f} mm}}"
configurations = "\n".join(
    f"    {format_str.format(c['idx'], c['name'], c['value'])}"
    for c in vampires_focus.configurations
)

__doc__ = f"""Usage:
    vampires_focus [-h | --help]
    vampires_focus [-w | --wait] (status|position|home|goto|nudge|stop|reset) [<pos>]

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
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
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        idx, name = vampires_focus.get_configuration()
        print(format_str.format(idx, name, vampires_focus.position))
    elif args["position"]:
        print(vampires_focus.position)
    elif args["home"]:
        vampires_focus.home(wait=args["--wait"])
    elif args["goto"]:
        pos = float(args["<pos>"])
        vampires_focus.move_absolute(pos, wait=args["--wait"])
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_focus.move_relative(rel_pos, wait=args["--wait"])
    elif args["stop"]:
        vampires_focus.stop()
    elif args["reset"]:
        vampires_focus.reset()


if __name__ == "__main__":
    main()
