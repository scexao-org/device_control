from docopt import docopt
import os
import sys
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

__doc__ = f"""Usage:
    vampires_qwp [-h | --help]
    vampires_qwp [-w | --wait] status
    vampires_qwp [-w | --wait] 1 (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_qwp [-w | --wait] 2 (status|position|home|goto|nudge|stop|reset) [<pos>]

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
    status          Returns the current status of the QWP wheel
    position        Returns the current position of the QWP wheel, in deg
    home            Homes the stage
    goto  <pos>     Move the stage to the given angle
    nudge <pos>     Move the stage relatively by the given angle
    stop            Stop the stage
    reset           Reset the stage"""

# setp 4. action
def main():
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
        return

    if args["1"]:
        vampires_qwp = connect(PYRO_KEYS["qwp1"])
    elif args["2"]:
        vampires_qwp = connect(PYRO_KEYS["qwp2"])
    elif args["status"]:
        for key in ("qwp1", "qwp2"):
            qwp = connect(PYRO_KEYS[key])
            print(f"{key.upper()}: {qwp.position:5.01f} deg")
        return

    if args["status"]:
        pos = vampires_qwp.position
        print(f"{pos:5.01f} deg")
    elif args["position"]:
        print(vampires_qwp.position)
    elif args["home"]:
        vampires_qwp.home(wait=args["--wait"])
    elif args["goto"]:
        pos = float(args["<pos>"])
        vampires_qwp.move_absolute(pos, wait=args["--wait"])
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_qwp.move_relative(rel_pos, wait=args["--wait"])
    elif args["stop"]:
        vampires_qwp.stop()
    elif args["reset"]:
        vampires_qwp.reset()


if __name__ == "__main__":
    main()
