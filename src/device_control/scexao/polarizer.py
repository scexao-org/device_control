import os
import sys

from device_control.drivers import CONEXDevice
from docopt import docopt
from scxconf.pyrokeys import SCEXAO

from swmain.redis import update_keys


class SCEXAOPolarizer(CONEXDevice):
    CONF = "scexao/conf_scexao_polarizer.toml"
    PYRO_KEY = SCEXAO.POL
    format_str = "{0:2d}: {1:6.2f} deg {{th={2:6.2f} deg}}"

    def _update_keys(self, posn):
        update_keys(X_POLARP=posn)

    def move_absolute(self, value, **kwargs):
        return super().move_absolute(value % 360, **kwargs)

    def help_message(self):
        return f"""Usage:
    scexao_polarizer [-h | --help]
    scexao_polarizer (status|position|home|goto|nudge|stop|reset) [<angle>]

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
"""


# setp 4. action
def main():
    scexao_pol = SCEXAOPolarizer.connect(os.getenv("WHICHCOMP") == "2")
    __doc__ = scexao_pol.help_message()
    args = docopt(__doc__, options_first=True)
    posns = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["position"] or args["status"]:
        posn = scexao_pol.get_position()
        print(posn)
    elif args["home"]:
        scexao_pol.home()
    elif args["goto"]:
        angle = float(args["<angle>"])
        scexao_pol.move_absolute(angle)
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        scexao_pol.move_relative(rel_angle)
    elif args["stop"]:
        scexao_pol.stop()
    elif args["reset"]:
        scexao_pol.reset()
    scexao_pol.update_keys(posns)


if __name__ == "__main__":
    main()
