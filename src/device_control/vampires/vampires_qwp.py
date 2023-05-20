import os
import sys

from docopt import docopt

from device_control.drivers import CONEXDevice
from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from swmain.redis import update_keys

class VAMPIRESQWP(CONEXDevice):
    format_str = "{0:1d}: {1:8s}"

    def __init__(self, number, **kwargs):
        super().__init__(**kwargs)
        if not number in (1, 2):
            raise ValueError("VAMPIRES only has QWP1 and QWP2")
        self.number = number

    def _move_absolute(self, value: float, **kwargs):
        super()._move_absolute(value, **kwargs)
        self.update_keys()

    def update_keys(self):
        pos = self._get_position()
        kwargs = {
            f"U_QWP{self.number:1d}": pos + self.offset,
            f"U_QWP{self.number:1d}TH": pos 
        }
        update_keys(**kwargs)


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
            print(f"{key.upper()}: {qwp.get_position():5.01f} deg")
            qwp.update_keys()
        return

    if args["status"]:
        pos = vampires_qwp.get_position()
        print(f"{pos:5.01f} deg")
    elif args["position"]:
        print(vampires_qwp.get_position())
    elif args["home"]:
        vampires_qwp.home(wait=args["--wait"])
    elif args["goto"]:
        pos = float(args["<pos>"])
        vampires_qwp.move_absolute(pos % 360, wait=args["--wait"])
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_qwp.move_relative(rel_pos, wait=args["--wait"])
    elif args["stop"]:
        vampires_qwp.stop()
    elif args["reset"]:
        vampires_qwp.reset()


if __name__ == "__main__":
    main()
