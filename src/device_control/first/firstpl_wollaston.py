import os
import sys

from docopt import docopt
# from scxconf.pyrokeys import VAMPIRES
from swmain.redis import update_keys

from device_control.drivers import CONEXDevice


class FIRSTPLWollaston(CONEXDevice):
    CONF = "first/conf_firstpl_wollaston.toml"
    PYRO_KEY = "FIRSTPL_WOLLASTON"
    format_str = "{0}: {1:10s} {{{2:5.02f} mm}}"

    def _update_keys(self, position):
        _, name = self.get_configuration(position=position)
        update_keys(X_FIRWOL=name.upper(), X_FIRWOF=position)

    def help_message(self):
        configurations = "\n".join(
            f"    {FIRSTPLWollaston.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    firstpl_wollaston [-h | --help]
    firstpl_wollaston (status|position|home|goto|nudge|stop|reset) [<pos>]
    firstpl_wollaston <configuration>

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
    firstpl_wollaston = FIRSTPLWollaston.connect(os.getenv("WHICHCOMP") == "K")
    __doc__ = firstpl_wollaston.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        posn, status = firstpl_wollaston.get_status()
        print(status)
    elif args["position"]:
        posn = firstpl_wollaston.get_position()
        print(posn)
    elif args["home"]:
        firstpl_wollaston.home()
    elif args["goto"]:
        pos = float(args["<pos>"])
        firstpl_wollaston.move_absolute(pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        firstpl_wollaston.move_relative(rel_pos)
    elif args["stop"]:
        firstpl_wollaston.stop()
    elif args["reset"]:
        firstpl_wollaston.reset()
    elif args["<configuration>"]:
        firstpl_wollaston.move_configuration(args["<configuration>"])
    firstpl_wollaston.update_keys(posn)


if __name__ == "__main__":
    main()
