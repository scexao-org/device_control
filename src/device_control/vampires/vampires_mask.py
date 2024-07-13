import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VAMPIRES
from swmain.redis import update_keys

from device_control.multi_device import MultiDevice


class VAMPIRESMaskWheel(MultiDevice):
    CONF = "vampires/conf_vampires_mask.toml"
    PYRO_KEY = VAMPIRES.MASK
    format_str = "{0:}: {1:17s} {{x={2:6.3f} mm, y={3:6.3f} mm, th={4:6.2f} deg}}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices["x"]._update_keys = lambda p: update_keys(U_MASKX=p)
        self.devices["y"]._update_keys = lambda p: update_keys(U_MASKY=p)
        self.devices["theta"]._update_keys = lambda p: update_keys(U_MASKTH=p)

    def _update_keys(self, positions):
        _, name = self.get_configuration(positions=positions)
        update_keys(U_MASK=name)

    def move_absolute(self, name, value, **kwargs):
        if name == "theta":
            value %= 360
        return super().move_absolute(name, value, **kwargs)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value']['x'], c['value']['y'], c['value']['theta'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_mask [-h | --help]
    vampires_mask status
    vampires_mask x (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_mask y (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_mask theta (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_mask <configuration>

Options:
    -h, --help   Show this screen

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
    vampires_mask = VAMPIRESMaskWheel.connect(os.getenv("WHICHCOMP") == "V")
    __doc__ = vampires_mask.help_message()
    args = docopt(__doc__, options_first=True)
    posns = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif len(sys.argv) == 2 and args["status"]:
        posns, status = vampires_mask.get_status()
        print(status)
        vampires_mask.update_keys(posns)
        return
    elif args["x"]:
        substage = "x"
    elif args["y"]:
        substage = "y"
    elif args["theta"]:
        substage = "theta"
    elif args["<configuration>"]:
        index = args["<configuration>"]
        return vampires_mask.move_configuration(index)
    if args["status"] or args["position"]:
        print(vampires_mask.get_position(substage))
    elif args["home"]:
        vampires_mask.home(substage)
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        vampires_mask.move_absolute(substage, new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_mask.move_relative(substage, rel_pos)
    elif args["stop"]:
        vampires_mask.stop(substage)
    elif args["reset"]:
        substage.reset()
    vampires_mask.update_keys(posns)


if __name__ == "__main__":
    main()
