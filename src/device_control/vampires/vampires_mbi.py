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


class VAMPIRESMBIWheel(CONEXDevice):
    format_str = "{0}: {1:15s} {{{2:6.02f} deg}}"

    def _update_keys(self, theta):
        _, name = self.get_configuration(position=theta)
        update_keys(U_MBI=name, U_MBITH=theta)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_mbi [-h | --help]
    vampires_mbi [-w | --wait] (status|position|home|goto|nudge|stop|reset) [<angle>]
    vampires_mbi [-w | --wait] <configuration>

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

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
    if os.getenv("WHICHCOMP") == "V":
        vampires_mbi = VAMPIRESMBIWheel.from_config(
            conf_dir / "vampires" / "conf_vampires_mbi.toml"
        )
    else:
        vampires_mbi = connect(PYRO_KEYS["vampires_mbi"])
    __doc__ = vampires_mbi.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["status"]:
        posn = vampires_mbi.get_position()
        idx, name = vampires_mbi.get_configuration(posn)
        print(VAMPIRESMBIWheel.format_str.format(idx, name, posn))
    elif args["position"]:
        print(vampires_mbi.get_position())
    elif args["home"]:
        if args["--wait"]:
            vampires_mbi.home()
        else:
            vampires_mbi.home()
    elif args["goto"]:
        angle = float(args["<angle>"])
        if args["--wait"]:
            vampires_mbi.move_absolute(angle % 360)
        else:
            vampires_mbi.move_absolute(angle % 360)
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        if args["--wait"]:
            vampires_mbi.move_relative(rel_angle)
        else:
            vampires_mbi.move_relative(rel_angle)
    elif args["stop"]:
        vampires_mbi.stop()
    elif args["reset"]:
        vampires_mbi.reset()
    elif args["<configuration>"]:
        try:
            index = int(args["<configuration>"])
        except ValueError:
            vampires_mbi.move_configuration_name(args["<configuration>"])
        vampires_mbi.move_configuration_idx(index)


if __name__ == "__main__":
    main()
