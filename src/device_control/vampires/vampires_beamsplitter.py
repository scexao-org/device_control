from docopt import docopt
import os
import sys
from swmain.network.pyroclient import connect # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

beamsplitter = connect(PYRO_KEYS["beamsplitter"])
configurations = "\n".join(f"    {c['idx']}: {c['name']:15s} {{{c['value']} deg}}" for c in beamsplitter.configurations)

__doc__ = f"""Usage:
    vampires_beamsplitter [-h | --help]
    vampires_beamsplitter [-w | --wait] (status|target|home|goto|nudge|stop|reset) [<angle>]
    vampires_beamsplitter [-w | --wait] <configuration>

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Wheel commands:
    status          Returns the current position of the beamsplitter wheel, in deg
    target          Returns the target position of the beamsplitter wheel, in deg
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
    if args["status"]:
        print(beamsplitter.position)
    elif args["target"]:
        print(beamsplitter.target_position)
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
        index = int(args["<configuration>"])
        beamsplitter.move_configuration(index, wait=args["--wait"])

if __name__ == "__main__":
    main()