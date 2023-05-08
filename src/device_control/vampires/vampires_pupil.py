from docopt import docopt
import os
import sys
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

vampires_pupil = connect(PYRO_KEYS["pupil"])

format_str = "{0}: {1:17s} {{x={2:6d} stp, y={3:6d} stp, th={4:5.1f} deg}}"
configurations = "\n".join(
    f"    {format_str.format(c['idx'], c['name'], c['value']['x'], c['value']['y'], c['value']['theta'])}"
    for c in vampires_pupil.configurations
)

__doc__ = f"""Usage:
    vampires_pupil [-h | --help]
    vampires_pupil [-h | --help] status
    vampires_pupil [-w | --wait] x (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_pupil [-w | --wait] y (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_pupil [-w | --wait] theta (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_pupil [-w | --wait] <configuration>

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
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    elif len(sys.argv) == 2 and args["status"]:
        idx, name = vampires_pupil.get_configuration()
        x = vampires_pupil.devices["x"].position
        y = vampires_pupil.devices["y"].position
        th = vampires_pupil.devices["theta"].position
        print(format_str.format(idx, name, x, y, th))
    elif args["x"]:
        substage = vampires_pupil.devices["x"]
    elif args["y"]:
        substage = vampires_pupil.devices["y"]
    elif args["theta"]:
        substage = vampires_pupil.devices["theta"]
    elif args["<configuration>"]:
        index = int(args["<configuration>"])
        return vampires_pupil.move_configuration(index, wait=args["--wait"])
    if args["status"] or args["position"]:
        print(substage.position)
    elif args["home"]:
        substage.home(wait=args["--wait"])
    elif args["goto"]:
        pos = float(args["<pos>"])
        substage.move_absolute(pos, wait=args["--wait"])
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        substage.move_relative(rel_pos, wait=args["--wait"])
    elif args["stop"]:
        substage.stop()
    elif args["reset"]:
        substage.reset()


if __name__ == "__main__":
    main()
