import os
import sys

from device_control.drivers import ThorlabsWheel
from device_control.pyro_keys import VAMPIRES
from device_control.vampires import connect_cameras
from docopt import docopt
from swmain.network.pyroclient import connect
from swmain.redis import update_keys


class VAMPIRESFilter(ThorlabsWheel):
    CONF = "vampires/conf_vampires_filter.toml"
    PYRO_KEY = VAMPIRES.FILT
    format_str = "{0:1d}: {1:8s}"

    def __init__(self, serial_kwargs, **kwargs):
        super().__init__(serial_kwargs, **kwargs)
        self.cams = connect_cameras()

    def _update_keys(self, position):
        pos, name = self.get_configuration(position=position)
        update_keys(U_FILTER=name, U_FILTTH=pos)
        for cam in self.cams:
            if cam is not None:
                cam.set_keyword("FILTER01", name)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_filter [-h | --help]
    vampires_filter (status|position)
    vampires_filter <slot>

Options:
    -h, --help   Show this screen

Stage commands:
    <slot>          Moves the filter wheel to the given slot, either a number or a filter name
    status          Returns the current filter name
    position        Returns the current filter slot

Configurations:
{configurations}"""


# setp 4. action
def main():
    vampires_filter = VAMPIRESFilter.connect(os.getenv("WHICHCOMP") == "V")
    __doc__ = vampires_filter.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif args["status"]:
        posn = vampires_filter.get_position()
        name = vampires_filter.get_status(posn)
        print(vampires_filter.format_str.format(posn, name))
    elif args["position"]:
        posn = vampires_filter.get_position()
        print(posn)
    elif args["<slot>"]:
        vampires_filter.move_configuration(args["<slot>"])
    vampires_filter.update_keys(posn)


if __name__ == "__main__":
    main()
