from docopt import docopt
import os
import sys

from swmain.devices.drivers.conex import CONEXDevice

conf_dir = os.path.abspath(os.getenv("CONF_DIR", f"{os.getenv('HOME')}/src/software-main/conf/"))
path = os.path.join(conf_dir, "devices/vampires/conf_vampires_beamsplitter.toml")
vampires_beamsplitter = CONEXDevice.from_config(path)

configurations = "\n".join(f"    {c['idx']}: {c['name']:15s} {{{c['value']} {vampires_beamsplitter.unit}}}" for c in vampires_beamsplitter.configurations)

__doc__ = f"""Usage:
    vampires_beamsplitter [-h | --help]
    vampires_beamsplitter [-w | --wait] (status|target|home|goto|nudge|stop|reset) [<angle>]
    vampires_beamsplitter [-w | --wait] <configuration>

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Wheel commands:
    status          Returns the current position of the beamsplitter wheel, in {vampires_beamsplitter.unit}
    target          Returns the target position of the beamsplitter wheel, in {vampires_beamsplitter.unit}
    home            Homes the beamsplitter wheel
    goto  <angle>   Move the beamsplitter wheel to the given angle, in {vampires_beamsplitter.unit}
    nudge <angle>   Move the beamsplitter wheel relatively by the given angle, in {vampires_beamsplitter.unit}
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
        print(vampires_beamsplitter.position)
    elif args["target"]:
        print(vampires_beamsplitter.target_position)
    elif args["home"]:
        vampires_beamsplitter.home(wait=args["--wait"])
    elif args["goto"]:
        angle = float(args["<angle>"])
        vampires_beamsplitter.move_absolute(angle, wait=args["--wait"])
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        vampires_beamsplitter.move_relative(rel_angle, wait=args["--wait"])
    elif args["stop"]:
        vampires_beamsplitter.stop()
    elif args["reset"]:
        vampires_beamsplitter.reset()
    elif args["<configuration>"]:
        index = int(args["<configuration>"])
        vampires_beamsplitter.move_configuration(index, wait=args["--wait"])

if __name__ == "__main__":
    main()