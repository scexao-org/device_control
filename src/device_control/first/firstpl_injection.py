import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VAMPIRES
from swmain.redis import update_keys

from device_control.multi_device import MultiDevice


class FIRSTPLInjection(MultiDevice):
    CONF = "first/conf_firstpl_injection.toml"
    PYRO_KEY = "FIRSTPL_INJECTION"
    format_str = "{0:}: {1:17s} {{x={2:06.0f} step, y={3:06.0f} step, f={4:6.02f} mm}}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices["x"]._update_keys = lambda p: update_keys(X_FIRINX=p)
        self.devices["y"]._update_keys = lambda p: update_keys(X_FIRINY=p)
        self.devices["f"]._update_keys = lambda p: update_keys(X_FIRINF=p)

    def _update_keys(self, positions):
        _, name = self.get_configuration(positions=positions)
        update_keys(U_MAX_FIRINJSK=name)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value']['x'], c['value']['y'], c['value']['f'])}"
            for c in self.configurations
        )
        return f"""Usage:
    firstpl_inj [-h | --help]
    firstpl_inj (status|home|stop)
    firstpl_inj x (status|position|home|goto|nudge|stop|reset) [<pos>]
    firstpl_inj y (status|position|home|goto|nudge|stop|reset) [<pos>]
    firstpl_inj f (status|position|home|goto|nudge|stop|reset) [<pos>]
    firstpl_inj <configuration>

Options:
    -h, --help   Show this screen

    
Commands:
    status          Returns the status of all stages
    home            Homes all stages
    stop            Immediately stops all stages
    
Stage commands:
    status          Returns the status of the stage
    position        Returns the current position of the stage
    home            Homes the stage
    goto  <pos>     Move the stage to the given position
    nudge <pos>     Move the stage relatively by the given position
    stop            Stop the stage
    reset           Reset the stage

Configurations:
{configurations}"""


# setp 4. action
def main():
    firstpl_injection = FIRSTPLInjection.connect(os.getenv("WHICHCOMP") == "K")
    __doc__ = firstpl_injection.help_message()
    args = docopt(__doc__, options_first=True)
    posns = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif len(sys.argv) == 2 and args["status"]:
        posns, status = firstpl_injection.get_status()
        print(status)
        firstpl_injection.update_keys(posns)
        return
    elif len(sys.argv) == 2 and args["home"]:
        firstpl_injection.home_all()
        return
    elif len(sys.argv) == 2 and args["stop"]:
        firstpl_injection.stop_all()
        return
    elif args["x"]:
        substage = "x"
    elif args["y"]:
        substage = "y"
    elif args["f"]:
        substage = "f"
    elif args["<configuration>"]:
        index = args["<configuration>"]
        return firstpl_injection.move_configuration(index)
    if args["status"] or args["position"]:
        print(firstpl_injection.get_position(substage))
    elif args["home"]:
        firstpl_injection.home(substage)
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        firstpl_injection.move_absolute(substage, new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        firstpl_injection.move_relative(substage, rel_pos)
    elif args["stop"]:
        firstpl_injection.stop(substage)
    elif args["reset"]:
        substage.reset()
    firstpl_injection.update_keys(posns)


if __name__ == "__main__":
    main()
