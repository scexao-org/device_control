import os
import sys

from docopt import docopt

from device_control.drivers import CONEXDevice
from device_control.pyro_keys import VAMPIRES
from device_control.vampires.cameras import connect_cameras
from swmain.network.pyroclient import \
    connect  # Requires scxconf and will fetch the IP addresses there.
from swmain.redis import update_keys


class VAMPIRESDiffWheel(CONEXDevice):
    CONF = "vampires/conf_vampires_diffwheel.toml"
    PYRO_KEY = VAMPIRES.DIFF
    format_str = "{0}: {1:22s} {{{2:5.01f} deg}}"

    def __init__(self, device_address=1, delay=0.1, **kwargs):
        super().__init__(device_address, delay, **kwargs)
        self.cams = connect_cameras()

    def _update_keys(self, theta):
        _, status = self.get_configuration(position=theta)
        if status == "Unknown":
            state1 = state2 = "Unknown"
        else:
            state1, state2 = status.split(" / ")
        update_keys(
            U_DIFFL1=state1,
            U_DIFFL2=state2,
            U_DIFFTH=theta,
        )
        for cam, state in zip(self.cams, (state1, state2)):
            if cam is not None:
                cam.set_keyword("FILTER02", state)

    def _move_absolute(self, value: float, wait=True):
        return super()._move_absolute(value % 360, wait)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_diffwheel [-h | --help]
    vampires_diffwheel (status|position|home|goto|nudge|stop|reset) [<angle>]
    vampires_diffwheel <configuration>

Options:
    -h, --help   Show this screen

Wheel commands:
    status          Returns the current status of the differential filter wheel
    position        Returns the current position of the differential filter wheel, in deg
    home            Homes the differential filter wheel
    goto  <angle>   Move the differential filter wheel to the given angle, in deg
    nudge <angle>   Move the differential filter wheel relatively by the given angle, in deg
    stop            Stop the differential filter wheel
    reset           Reset the differential filter wheel
        
Configurations (cam1 / cam2):
{configurations}"""


# setp 4. action
def main():
    vampires_diffwheel = VAMPIRESDiffWheel.connect(os.getenv("WHICHCOMP") == "V")
    __doc__ = vampires_diffwheel.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        posn = vampires_diffwheel.get_position()
        idx, name = vampires_diffwheel.get_configuration(posn)
        print(vampires_diffwheel.format_str.format(idx, name, posn))
    elif args["position"]:
        print(vampires_diffwheel.get_position())
    elif args["home"]:
        vampires_diffwheel.home()
    elif args["goto"]:
        angle = float(args["<angle>"])
        vampires_diffwheel.move_absolute(angle % 360)
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        vampires_diffwheel.move_relative(rel_angle)
    elif args["stop"]:
        vampires_diffwheel.stop()
    elif args["reset"]:
        vampires_diffwheel.reset()
    elif args["<configuration>"]:
        vampires_diffwheel.move_configuration(args["<configuration>"])
    vampires_diffwheel.update_keys(posn)


if __name__ == "__main__":
    main()
