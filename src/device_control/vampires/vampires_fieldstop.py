import os
import sys

from docopt import docopt

from device_control.multi_device import MultiDevice
from device_control.pyro_keys import VAMPIRES
from swmain.redis import update_keys

__all__ = ["VAMPIRESFieldstop"]


class VAMPIRESFieldstop(MultiDevice):
    CONF = "vampires/conf_vampires_fieldstop.toml"
    PYRO_KEY = VAMPIRES.FIELDSTOP
    format_str = "{0:}: {1:17s} {{x={2:6.3f} mm, y={3:6.3f} mm}}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices["x"]._update_keys = lambda p: update_keys(U_FLDSTX=p, X_VAMFSX=p)
        self.devices["y"]._update_keys = lambda p: update_keys(U_FLDSTY=p, X_VAMFSY=p)

    def _update_keys(self, positions):
        _, name = self.get_configuration(positions=positions)
        update_keys(U_FLDSTP=name, X_VAMFST=name)  # deprecated

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value']['x'], c['value']['y'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_fieldstop [-h | --help]
    vampires_fieldstop status
    vampires_fieldstop x (status|target|home|goto|nudge|stop|reset) [<pos>]
    vampires_fieldstop y (status|target|home|goto|nudge|stop|reset) [<pos>]
    vampires_fieldstop <configuration>

Options:
    -h, --help   Show this screen

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
    fieldstop = VAMPIRESFieldstop.connect(local=os.getenv("WHICHCOMP", None) == "V")
    __doc__ = fieldstop.help_message()
    args = docopt(__doc__, options_first=True)
    posns = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif len(sys.argv) == 2 and args["status"]:
        idx, name = fieldstop.get_configuration()
        x = fieldstop.get_position("x")
        y = fieldstop.get_position("y")
        posns = (x, y)
        print(fieldstop.format_str.format(idx, name, x, y))
        fieldstop.update_keys(posns)
        return
    elif args["x"]:
        substage = "x"
    elif args["y"]:
        substage = "y"
    elif args["<configuration>"]:
        index = args["<configuration>"]
        return fieldstop.move_configuration(index)

    if args["status"] or args["position"]:
        print(fieldstop.get_position(substage))
    elif args["home"]:
        fieldstop.home(substage)
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        fieldstop.move_absolute(substage, new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        fieldstop.move_relative(substage, rel_pos)
    elif args["stop"]:
        fieldstop.stop(substage)
    elif args["reset"]:
        substage.reset()
    fieldstop.update_keys(posns)


if __name__ == "__main__":
    main()
