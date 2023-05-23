import os
import sys

from docopt import docopt

from swmain.devices.multi_device import MultiDevice

conf_dir = os.path.abspath(
    os.getenv("CONF_DIR", f"{os.getenv('HOME')}/src/software-main/conf/")
)
path = os.path.join(conf_dir, "devices/vampires/conf_vampires_fieldstop.toml")
vampires_fieldstop = MultiDevice.from_config(path)

units = [d.unit for d in vampires_fieldstop.devices.values()]
lines = []
for config in vampires_fieldstop.configurations:
    line = f"    {config['idx']:2d}: {config['name']:23s} {{"
    iter = zip(config["value"].items(), units)
    line += ", ".join(f"{key}={value} {unit}" for (key, value), unit in iter)
    line += "}"
    lines.append(line)
configurations = "\n".join(lines)


__doc__ = f"""Usage:
    vampires_fieldstop [-h | --help]
    vampires_fieldstop [-w | --wait] x (status|target|home|goto|nudge|stop|reset) [<pos>]
    vampires_fieldstop [-w | --wait] y (status|target|home|goto|nudge|stop|reset) [<pos>]
    vampires_fieldstop [-w | --wait] <configuration>

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
    status          Returns the current position of the stage
    target          Returns the target position of the stage
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
    if args["x"]:
        sub = "x"
    elif args["y"]:
        sub = "y"
    elif args["<configuration>"]:
        index = int(args["<configuration>"])
        return vampires_fieldstop.move_configuration(index, wait=args["--wait"])
    if args["status"]:
        print(vampires_fieldstop[sub].position)
    elif args["target"]:
        print(vampires_fieldstop[sub].target_position)
    elif args["home"]:
        vampires_fieldstop[sub].home(wait=args["--wait"])
    elif args["goto"]:
        pos = float(args["<pos>"])
        vampires_fieldstop[sub].move_absolute(pos, wait=args["--wait"])
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_fieldstop[sub].move_relative(rel_pos, wait=args["--wait"])
    elif args["stop"]:
        vampires_fieldstop[sub].stop()
    elif args["reset"]:
        vampires_fieldstop[sub].reset()


if __name__ == "__main__":
    main()
