from typing import Union

import numpy as np
import tomli
import sys
from swmain.redis import update_keys
from device_control.multi_device import MultiDevice

from docopt import docopt

from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.


class VAMPIRESMaskWheel(MultiDevice):
    format_str = "{0:2d}: {1:17s} {{x={2:6.3f} mm, y={3:6.3f} mm, th={4:6.2f} deg}}"

    def _update_keys(self, positions):
        _, name = self.get_configuration(positions=positions)
        update_keys(
            U_MASK=name,
            U_MASKX=positions[0],
            U_MASKY=positions[1],
            U_MASKTH=positions[2],
        )

    def help_message(self):
        configurations = "\n".join(
            f"    {VAMPIRESMaskWheel.format_str.format(c['idx'], c['name'], c['value']['x'], c['value']['y'], c['value']['theta'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_mask [-h | --help]
    vampires_mask [-h | --help] status
    vampires_mask [-w | --wait] x (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_mask [-w | --wait] y (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_mask [-w | --wait] theta (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_mask [-w | --wait] <configuration>

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
    status          Returns the status of the stage
    position        Returns the current position of the stage
    home            Homes the stage
    goto  <pos>     Move the stage to the given angle
    nudge <pos>     Move the stage relatively by the given angle
    stop            Stop the stage
    reset           Reset the stage

Configurations:
{configurations}"""


# setp 4. action
def main():
    vampires_mask = connect(PYRO_KEYS["mask"])
    __doc__ = vampires_mask.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    elif len(sys.argv) == 2 and args["status"]:
        idx, name = vampires_mask.get_configuration()
        x = vampires_mask.get_position("x")
        y = vampires_mask.get_position("y")
        th = vampires_mask.get_position("theta")
        print(VAMPIRESMaskWheel.format_str.format(idx, name, x, y, th))
        return
    elif args["x"]:
        substage = "x"
    elif args["y"]:
        substage = "y"
    elif args["theta"]:
        substage = "theta"
    elif args["<configuration>"]:
        index = int(args["<configuration>"])
        return vampires_mask.move_configuration_idx(index, wait=args["--wait"])
    if args["status"] or args["position"]:
        print(vampires_mask.get_position(substage))
    elif args["home"]:
        vampires_mask.home(substage, wait=args["--wait"])
    elif args["goto"]:
        pos = float(args["<pos>"])
        if args["theta"]:
            vampires_mask.move_absolute(substage, pos % 360, wait=args["--wait"])
        else:
            vampires_mask.move_absolute(substage, pos, wait=args["--wait"])
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_mask.move_relative(substage, rel_pos, wait=args["--wait"])
    elif args["stop"]:
        vampires_mask.stop(substage)
    elif args["reset"]:
        substage.reset()


if __name__ == "__main__":
    main()
