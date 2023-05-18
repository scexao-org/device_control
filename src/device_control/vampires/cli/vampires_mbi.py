from docopt import docopt
import os
import sys
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

mbi = connect(PYRO_KEYS["mbi"])

format_str = "{0}: {1:15s} {{{2:5.01f} deg}}"
configurations = "\n".join(
    f"    {format_str.format(c['idx'], c['name'], c['value'])}"
    for c in mbi.configurations
)

__doc__ = f"""Usage:
    vampires_mbi [-h | --help]
    vampires_mbi [-w | --wait] (status|position|home|goto|nudge|stop|reset) [<angle>]
    vampires_mbi [-w | --wait] <configuration>

Options:
    -h, --help        Show this screen
    -w, --wait        Block command until position has been reached, for applicable commands
    <configuration>   Move device into specific configuration

Wheel commands:
    status          Returns the current status of the MBI wheel
    position        Returns the current position of the MBI wheel, in deg
    home            Homes the MBI wheel
    goto  <angle>   Move the MBI wheel to the given angle, in deg
    nudge <angle>   Move the MBI wheel relatively by the given angle, in deg
    stop            Stop the MBI wheel
    reset           Reset the MBI wheel
        
Configurations:
{configurations}"""

# setp 4. action
def main():
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["status"]:
        idx, name = mbi.get_configuration()
        print(f"{idx}: {name} {{{mbi.position:5.01f} {mbi.unit}}}")
    elif args["position"]:
        print(mbi.position)
    elif args["home"]:
        mbi.home(wait=args["--wait"])
    elif args["goto"]:
        angle = float(args["<angle>"])
        mbi.move_absolute(angle % 360, wait=args["--wait"])
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        mbi.move_relative(rel_angle, wait=args["--wait"])
    elif args["stop"]:
        mbi.stop()
    elif args["reset"]:
        mbi.reset()
    elif args["<configuration>"]:
        try:
            index = int(args["<configuration>"])
            mbi.move_configuration_idx(index, wait=args["--wait"])
        except ValueError:
            mbi.move_configuration_name(args["<configuration>"], wait=args["--wait"])


if __name__ == "__main__":
    main()
