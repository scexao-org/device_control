import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VISWFS

from device_control.drivers import CONEXDevice
from swmain.redis import update_keys


class VISWFSRotStage2(CONEXDevice):
    """
    VISWFS Rotation Stage 2

    Controls the CONEX rotation stage for the rotation stage cube wheel. Inside this wheel there are three optics installed:
    1. Dichroic filter
    2. Polarizing beamsplitter cube (PBS)
    3. Mirror
    
    """

    CONF = "viswfs/conf_viswfs_rs2.toml"
    PYRO_KEY = VISWFS.RS2
    format_str = "{0}: {1:15s} {{{2:5.01f} deg}}"

    def _update_keys(self, theta):
        _, name = self.get_configuration(position=theta)
        update_keys(U_RS2=name, U_RS2TH=theta)

    def _move_absolute(self, value: float):
        # make sure to mod360 the input value
        return super()._move_absolute(value % 360)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    viswfs_rs2 [-h | --help]
    viswfs_rs2 (status|position|home|goto|nudge|stop|reset) [<angle>]
    viswfs_rs2 <configuration>

Options:
    -h, --help   Show this screen

Wheel commands:
    status          Returns the current status of the rotation stage wheel
    position        Returns the current position of the rotation stage wheel, in deg
    home            Homes the rotation stage wheel
    goto  <angle>   Move the rotation stage wheel to the given angle, in deg
    nudge <angle>   Move the rotation stage wheel relatively by the given angle, in deg
    stop            Stop the rotation stage wheel
    reset           Reset the rotation stage wheel

Configurations:
{configurations}"""


def main():
    rotation_stage = VISWFSRotStage2.connect(local=os.getenv("WHICHCOMP"))
    __doc__ = rotation_stage.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["status"]:
        posn, status = rotation_stage.get_status()
        print(status)
    elif args["position"]:
        posn = rotation_stage.get_position()
        print(posn)
    elif args["home"]:
        rotation_stage.home()
    elif args["goto"]:
        angle = float(args["<angle>"])
        rotation_stage.move_absolute(angle)
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        rotation_stage.move_relative(rel_angle)
    elif args["stop"]:
        rotation_stage.stop()
    elif args["reset"]:
        rotation_stage.reset()
    elif args["<configuration>"]:
        rotation_stage.move_configuration(args["<configuration>"])
    rotation_stage.update_keys(posn)


if __name__ == "__main__":
    main()
