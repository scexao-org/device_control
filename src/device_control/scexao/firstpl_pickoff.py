import os
import sys

from docopt import docopt
# from scxconf.pyrokeys import VAMPIRES
from swmain.redis import update_keys

from device_control.drivers import CONEXDevice


class FIRSTPLPickoff(CONEXDevice):
    CONF = "scexao/conf_firstpl_pickoff.toml"
    PYRO_KEY = "FIRSTPL_PICKOFF" # Check later
    format_str = "{0}: {1:10s} {{{2:5.02f} mm}}"

    def _update_keys(self, position):
        _, name = self.get_configuration(position=position)
        update_keys(X_FIRPKO=name.upper(), X_FIRPKP=position)

    def help_message(self):
        configurations = "\n".join(
            f"    {FIRSTPLPickoff.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    firstpl_pickoff [-h | --help]
    firstpl_pickoff (status|position|home|goto|nudge|stop|reset) [<pos>]
    firstpl_pickoff <configuration>

Options:
    -h, --help   Show this screen

Stage commands:
    status          Returns the current status of the focus stage
    position        Returns the current position of the focus stage, in mm
    home            Homes the focus stage
    goto  <pos>     Move the focus stage to the given position, in mm
    nudge <pos>     Move the focus stage relatively by the given position, in mm
    stop            Stop the focus stage
    reset           Reset the focus stage

Configurations:
{configurations}"""


# setp 4. action
def main():
    firstpl_pickoff = FIRSTPLPickoff.connect(os.getenv("WHICHCOMP") == "2")
    __doc__ = firstpl_pickoff.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        posn, status = firstpl_pickoff.get_status()
        print(status)
    elif args["position"]:
        posn = firstpl_pickoff.get_position()
        print(posn)
    elif args["home"]:
        firstpl_pickoff.home()
    elif args["goto"]:
        pos = float(args["<pos>"])
        firstpl_pickoff.move_absolute(pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        firstpl_pickoff.move_relative(rel_pos)
    elif args["stop"]:
        firstpl_pickoff.stop()
    elif args["reset"]:
        firstpl_pickoff.reset()
    elif args["<configuration>"]:
        firstpl_pickoff.move_configuration(args["<configuration>"])
    firstpl_pickoff.update_keys(posn)


if __name__ == "__main__":
    main()
