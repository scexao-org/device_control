import os
import sys

from docopt import docopt

from device_control.drivers import CONEXDevice
from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from swmain.redis import update_keys


class VAMPIRESBeamsplitter(CONEXDevice):
    format_str = "{0}: {1:15s} {{{2:5.01f} deg}}"

    def home(self, **kwargs):
        super().home(**kwargs)
        self.update_keys()

    def _move_absolute(self, value: float, **kwargs):
        super()._move_absolute(value, **kwargs)
        self.update_keys()

    def move_relative(self, value: float, **kwargs):
        super().move_relative(value, **kwargs)
        self.update_keys()

    def update_keys(self):
        posn = self.get_position()
        _, name = self.get_configuration()
        update_keys(U_BS=name, U_BSTH=posn)

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
    beamsplitter = connect(PYRO_KEYS["beamsplitter"])
    __doc__ = beamsplitter.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["status"]:
        idx, name = beamsplitter.get_configuration()
        print(
            f"{idx}: {name} {{{beamsplitter.get_position():5.01f} {beamsplitter.get_unit()}}}"
        )
    elif args["position"]:
        print(beamsplitter.get_position())
    elif args["home"]:
        if args["--wait"]:
            beamsplitter.home()
        else:
            beamsplitter.home__oneway()
    elif args["goto"]:
        angle = float(args["<angle>"])
        if args["--wait"]:
            beamsplitter.move_absolute(angle % 360)
        else:
            beamsplitter.move_absolute__oneway(angle % 360)
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        if args["--wait"]:
            beamsplitter.move_relative(rel_angle)
        else:
            beamsplitter.move_relative__oneway(rel_angle)
    elif args["stop"]:
        beamsplitter.stop()
    elif args["reset"]:
        beamsplitter.reset()
    elif args["<configuration>"]:
        try:
            index = int(args["<configuration>"])
            beamsplitter.move_configuration_idx(index, wait=args["--wait"])
        except ValueError:
            beamsplitter.move_configuration_name(
                args["<configuration>"], wait=args["--wait"]
            )


if __name__ == "__main__":
    main()
