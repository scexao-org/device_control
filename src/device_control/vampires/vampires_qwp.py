from docopt import docopt
import os
import sys
from swmain.network.pyroclient import connect # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

vampires_qwp = connect(PYRO_KEYS["qwp"])
units = ["deg", "deg"]
lines = []
for config in vampires_qwp.configurations:
    line = f"    {config['idx']:2d}: {config['name']:11s} {{"
    iter = zip(config["value"].items(), units)
    line += ", ".join(f"{key}={value} {unit}" for (key, value), unit in iter)
    line += "}"
    lines.append(line)
configurations = "\n".join(lines)
    

__doc__ = f"""Usage:
    vampires_qwp [-h | --help]
    vampires_qwp [-w | --wait] 1 (status|target|home|goto|nudge|stop|reset) [<pos>]
    vampires_qwp [-w | --wait] 2 (status|target|home|goto|nudge|stop|reset) [<pos>]
    vampires_qwp [-w | --wait] <configuration>

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
    if args["1"]:
        sub = "1"
    elif args["2"]:
        sub = "2"
    elif args["<configuration>"]:
        index = int(args["<configuration>"])
        return vampires_qwp.move_configuration(index, wait=args["--wait"])
    if args["status"]:
        print(vampires_qwp[sub].position)
    elif args["target"]:
        print(vampires_qwp[sub].target_position)
    elif args["home"]:
        vampires_qwp[sub].home(wait=args["--wait"])
    elif args["goto"]:
        pos = float(args["<pos>"])
        vampires_qwp[sub].move_absolute(pos, wait=args["--wait"])
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_qwp[sub].move_relative(rel_pos, wait=args["--wait"])
    elif args["stop"]:
        vampires_qwp[sub].stop()
    elif args["reset"]:
        vampires_qwp[sub].reset()
   

if __name__ == "__main__":
    main()