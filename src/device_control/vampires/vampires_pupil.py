from docopt import docopt
import os
import sys
from swmain.network.pyroclient import connect # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

vampires_pupil = connect(PYRO_KEYS["pupil"])

units = ["step", "step", "deg"]
lines = []
for config in vampires_pupil.configurations:
    line = f"    {config['idx']:2d}: {config['name']:17s} {{"
    iter = zip(config["value"].items(), units)
    line += ", ".join(f"{key}={value} {unit}" for (key, value), unit in iter)
    line += "}"
    lines.append(line)
configurations = "\n".join(lines)
    

__doc__ = f"""Usage:
    vampires_pupil [-h | --help]
    vampires_pupil [-w | --wait] x (status|target|home|goto|nudge|stop|reset) [<pos>]
    vampires_pupil [-w | --wait] y (status|target|home|goto|nudge|stop|reset) [<pos>]
    vampires_pupil [-w | --wait] theta (status|target|home|goto|nudge|stop|reset) [<pos>]
    vampires_pupil [-w | --wait] <configuration>

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
    elif args["theta"]:
        sub = "theta"
    elif args["<configuration>"]:
        index = int(args["<configuration>"])
        return vampires_pupil.move_configuration(index, wait=args["--wait"])
    if args["status"]:
        print(vampires_pupil[sub].position)
    elif args["target"]:
        print(vampires_pupil[sub].target_position)
    elif args["home"]:
        vampires_pupil[sub].home(wait=args["--wait"])
    elif args["goto"]:
        pos = float(args["<pos>"])
        vampires_pupil[sub].move_absolute(pos, wait=args["--wait"])
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_pupil[sub].move_relative(rel_pos, wait=args["--wait"])
    elif args["stop"]:
        vampires_pupil[sub].stop()
    elif args["reset"]:
        vampires_pupil[sub].reset()
   

if __name__ == "__main__":
    main()