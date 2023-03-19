from docopt import docopt
import os
import sys

from swmain.devices.drivers.conex import CONEXDevice

conf_dir = os.path.abspath(os.getenv("CONF_DIR", f"{os.getenv('HOME')}/src/software-main/conf/"))
path = os.path.join(conf_dir, "devices/vampires/conf_vampires_diffwheel.toml")
vampires_diffwheel = CONEXDevice.from_config(path)

configurations = "\n".join(f"    {c['idx']}: {c['name']:21s} {{{c['value']} {vampires_diffwheel.unit}}}" for c in vampires_diffwheel.configurations)

__doc__ = f"""Usage:
    vampires_diffwheel [-h | --help]
    vampires_diffwheel [-w | --wait] (status|target|home|goto|nudge|stop|reset) [<angle>]
    vampires_diffwheel [-w | --wait] <configuration>

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Wheel commands:
    status          Returns the current position of the differential filter wheel, in {vampires_diffwheel.unit}
    target          Returns the target position of the differential filter wheel, in {vampires_diffwheel.unit}
    home            Homes the differential filter wheel
    goto  <angle>   Move the differential filter wheel to the given angle, in {vampires_diffwheel.unit}
    nudge <angle>   Move the differential filter wheel relatively by the given angle, in {vampires_diffwheel.unit}
    stop            Stop the differential filter wheel
    reset           Reset the differential filter wheel
        
Configurations (cam1 / cam2):
{configurations}"""

# setp 4. action
def main():
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        print(vampires_diffwheel.position)
    elif args["target"]:
        print(vampires_diffwheel.target_position)
    elif args["home"]:
        vampires_diffwheel.home(wait=args["--wait"])
    elif args["goto"]:
        angle = float(args["<angle>"])
        vampires_diffwheel.move_absolute(angle, wait=args["--wait"])
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        vampires_diffwheel.move_relative(rel_angle, wait=args["--wait"])
    elif args["stop"]:
        vampires_diffwheel.stop()
    elif args["reset"]:
        vampires_diffwheel.reset()
    elif args["<configuration>"]:
        index = int(args["<configuration>"])
        vampires_diffwheel.move_configuration(index, wait=args["--wait"])

if __name__ == "__main__":
    main()