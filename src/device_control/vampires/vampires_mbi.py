import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VAMPIRES

from device_control.drivers import CONEXDevice
from swmain.redis import update_keys


class VAMPIRESMBIWheel(CONEXDevice):
    CONF = "vampires/conf_vampires_mbi.toml"
    PYRO_KEY = VAMPIRES.MBI
    format_str = "{0}: {1:15s} {{{2:6.02f} deg}}"

    def _update_keys(self, theta):
        _, name = self.get_configuration(position=theta)
        update_keys(U_MBI=name, U_MBITH=theta)

    def _move_absolute(self, value: float):
        return super()._move_absolute(value % 360)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_mbi [-h | --help]
    vampires_mbi (status|position|home|goto|nudge|stop|reset) [<angle>]
    vampires_mbi <configuration>

Options:
    -h, --help   Show this screen

Wheel commands:
    status          Returns the current status of the MBI wheel
    position        Returns the current position of the MBI wheel, in deg
    home            Homes the MBI wheel
    goto  <angle>   Move the MBI wheel to the given angle, in deg
    nudge <angle>   Move the MBI wheel relatively by the given angle, in deg
    stop            Stop the MBI wheel
    reset           Reset the MBI wheel

Configurations:
{configurations}"""


def main():
    vampires_mbi = VAMPIRESMBIWheel.connect(os.getenv("WHICHCOMP") == "V")
    __doc__ = vampires_mbi.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["status"]:
        posn, status = vampires_mbi.get_status()
        print(status)
    elif args["position"]:
        posn = vampires_mbi.get_position()
        print(posn)
    elif args["home"]:
        vampires_mbi.home()
    elif args["goto"]:
        angle = float(args["<angle>"])
        vampires_mbi.move_absolute(angle)
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        vampires_mbi.move_relative(rel_angle)
    elif args["stop"]:
        vampires_mbi.stop()
    elif args["reset"]:
        vampires_mbi.reset()
    elif args["<configuration>"]:
        vampires_mbi.move_configuration(args["<configuration>"])
    vampires_mbi.update_keys(posn)


if __name__ == "__main__":
    main()
