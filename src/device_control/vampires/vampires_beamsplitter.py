from docopt import docopt
import os
import sys
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

beamsplitter = connect(PYRO_KEYS["beamsplitter"])

format_str = "{0}: {1:15s} {{{2:5.01f} deg}}"
configurations = "\n".join(
    f"    {format_str.format(c['idx'], c['name'], c['value'])}"
    for c in beamsplitter.configurations
)

__doc__ = f"""Usage:
    vampires_beamsplitter [-h | --help]
    vampires_beamsplitter [-w | --wait] (status|position|home|goto|nudge|stop|reset) [<angle>]
    vampires_beamsplitter [-w | --wait] <configuration>

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Wheel commands:
    status          Returns the current status of the beamsplitter wheel
    position        Returns the current position of the beamsplitter wheel, in deg
    home            Homes the beamsplitter wheel
    goto  <angle>   Move the beamsplitter wheel to the given angle, in deg
    nudge <angle>   Move the beamsplitter wheel relatively by the given angle, in deg
    stop            Stop the beamsplitter wheel
    reset           Reset the beamsplitter wheel
        
Configurations:
{configurations}"""

# setp 4. action
def main():
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["status"]:
        idx, name = beamsplitter.get_configuration()
        print(f"{idx}: {name} {{{beamsplitter.position:5.01f} {beamsplitter.unit}}}")
    elif args["position"]:
        print(beamsplitter.position)
    elif args["home"]:
        beamsplitter.home(wait=args["--wait"])
    elif args["goto"]:
        angle = float(args["<angle>"])
        beamsplitter.move_absolute(angle, wait=args["--wait"])
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        beamsplitter.move_relative(rel_angle, wait=args["--wait"])
    elif args["stop"]:
        beamsplitter.stop()
    elif args["reset"]:
        beamsplitter.reset()
    elif args["<configuration>"]:
        try:
            index = int(args["<configuration>"])
            beamsplitter.move_configuration_idx(index, wait=args["--wait"])
        except ValueError:
            beamsplitter.move_configuration_name(
                args["<configuration>"], wait=args["--wait"]
            )


if __name__ == "__main__":
    main()
