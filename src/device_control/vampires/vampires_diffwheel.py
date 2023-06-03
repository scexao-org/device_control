import os
import sys

from docopt import docopt

from device_control import conf_dir
from device_control.drivers import CONEXDevice
from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (  # Requires scxconf and will fetch the IP addresses there.
    connect,
)
from swmain.redis import update_keys


class VAMPIRESDiffWheel(CONEXDevice):
    format_str = "{0}: {1:22s} {{{2:5.01f} deg}}"

    def _update_keys(self, theta):
        _, status = self.get_configuration(position=theta)
        if status == "Unknown":
            update_keys(
                U_DIFFL1="Unknown",
                U_DIFFL2="Unknown",
                U_DIFFTH=theta,
            )
        else:
            state1, state2 = status.split(" / ")
            update_keys(
                U_DIFFL1=state1,
                U_DIFFL2=state2,
                U_DIFFTH=theta,
            )

    def help_message(self):
        configurations = "\n".join(
            f"    {VAMPIRESDiffWheel.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_diffwheel [-h | --help]
    vampires_diffwheel [-w | --wait] (status|position|home|goto|nudge|stop|reset) [<angle>]
    vampires_diffwheel [-w | --wait] <configuration>

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

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
    if os.getenv("WHICHCOMP") == "V":
        vampires_diffwheel = VAMPIRESDiffWheel.from_config(
            conf_dir / "vampires/conf_vampires_diffwheel.toml"
        )
    else:
        vampires_diffwheel = connect(PYRO_KEYS["diffwheel"])
    __doc__ = vampires_diffwheel.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        idx, name = vampires_diffwheel.get_configuration()
        print(VAMPIRESDiffWheel.format_str.format(idx, name, vampires_diffwheel.get_position()))
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
        try:
            index = int(args["<configuration>"])
        except ValueError:
            vampires_diffwheel.move_configuration_name(args["<configuration>"])
        vampires_diffwheel.move_configuration_idx(index)
    vampires_diffwheel.update_keys()


if __name__ == "__main__":
    main()
