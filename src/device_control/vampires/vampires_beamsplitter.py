import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VAMPIRES

from device_control.drivers import CONEXDevice
from swmain.redis import update_keys


class VAMPIRESBeamsplitter(CONEXDevice):
    """
    VAMPIRES Beamsplitter

    Controls the CONEX rotation stage for the beamsplitter cube wheel. Inside this wheel there are two optics installed:
    1. Polarizing beamsplitter cube (PBS)
    2. Non-polarizing beamsplitter cube (NPBS)

    For single-cam mode, choose any of the in-between angles to remove the beamsplitter.
    """

    CONF = "vampires/conf_vampires_beamsplitter.toml"
    PYRO_KEY = VAMPIRES.BS
    format_str = "{0}: {1:15s} {{{2:5.01f} deg}}"

    def _update_keys(self, theta):
        _, name = self.get_configuration(position=theta)
        update_keys(U_BS=name, U_BSTH=theta)

    def _move_absolute(self, value: float):
        # make sure to mod360 the input value
        return super()._move_absolute(value % 360)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_beamsplitter [-h | --help]
    vampires_beamsplitter (status|position|home|goto|nudge|stop|reset) [<angle>]
    vampires_beamsplitter <configuration>

Options:
    -h, --help   Show this screen

Wheel commands:
    status          Returns the current status of the beamsplitter wheel
    position        Returns the current position of the beamsplitter wheel, in deg
    home            Homes the beamsplitter wheel
    goto  <angle>   Move the beamsplitter wheel to the given angle, in deg
    nudge <angle>   Move the beamsplitter wheel relatively by the given angle, in deg
    stop            Stop the beamsplitter wheel
    reset           Reset the beamsplitter wheel

Configurations:
{configurations}"""


def main():
    beamsplitter = VAMPIRESBeamsplitter.connect(local=os.getenv("WHICHCOMP") == "V")
    __doc__ = beamsplitter.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["status"]:
        posn, status = beamsplitter.get_status()
        print(status)
    elif args["position"]:
        posn = beamsplitter.get_position()
        print(posn)
    elif args["home"]:
        beamsplitter.home()
    elif args["goto"]:
        angle = float(args["<angle>"])
        beamsplitter.move_absolute(angle)
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        beamsplitter.move_relative(rel_angle)
    elif args["stop"]:
        beamsplitter.stop()
    elif args["reset"]:
        beamsplitter.reset()
    elif args["<configuration>"]:
        beamsplitter.move_configuration(args["<configuration>"])
    beamsplitter.update_keys(posn)


if __name__ == "__main__":
    main()
