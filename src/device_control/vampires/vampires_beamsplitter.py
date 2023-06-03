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


class VAMPIRESBeamsplitter(CONEXDevice):
    format_str = "{0}: {1:15s} {{{2:5.01f} deg}}"

    def _update_keys(self, theta):
        _, name = self.get_configuration(position=theta)
        update_keys(U_BS=name, U_BSTH=theta)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_beamsplitter [-h | --help]
    vampires_beamsplitter [-w | --wait] (status|position|home|goto|nudge|stop|reset) [<angle>]
    vampires_beamsplitter [-w | --wait] <configuration>

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

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
    if os.getenv("WHICHCOMP") != "V":
        beamsplitter = connect(PYRO_KEYS["beamsplitter"])
    else:
        beamsplitter = VAMPIRESBeamsplitter.from_config(
            conf_dir / "vampires/conf_vampires_beamsplitter.toml"
        )
    __doc__ = beamsplitter.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["status"]:
        idx, name = beamsplitter.get_configuration()
        print(f"{idx}: {name} {{{beamsplitter.get_position():5.01f} {beamsplitter.get_unit()}}}")
    elif args["position"]:
        print(beamsplitter.get_position())
    elif args["home"]:
        if args["--wait"]:
            beamsplitter.home()
        else:
            beamsplitter.home()
    elif args["goto"]:
        angle = float(args["<angle>"])
        if args["--wait"]:
            beamsplitter.move_absolute(angle % 360)
        else:
            beamsplitter.move_absolute(angle % 360)
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        if args["--wait"]:
            beamsplitter.move_relative(rel_angle)
        else:
            beamsplitter.move_relative(rel_angle)
    elif args["stop"]:
        beamsplitter.stop()
    elif args["reset"]:
        beamsplitter.reset()
    elif args["<configuration>"]:
        try:
            index = int(args["<configuration>"])
            if args["--wait"]:
                beamsplitter.move_configuration_idx(index)
            else:
                beamsplitter.move_configuration_idx(index)
        except ValueError:
            if args["--wait"]:
                beamsplitter.move_configuration_name(args["<configuration>"])
            else:
                beamsplitter.move_configuration_name(args["<configuration>"])


if __name__ == "__main__":
    main()
