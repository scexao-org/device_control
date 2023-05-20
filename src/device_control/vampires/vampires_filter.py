import sys

from docopt import docopt

from device_control.drivers import ThorlabsWheel
from device_control.vampires import PYRO_KEYS
from swmain.redis import update_keys
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.


class VAMPIRESFilter(ThorlabsWheel):
    format_str = "{0:1d}: {1:8s}"

    def _move_absolute(self, value: float, **kwargs):
        super()._move_absolute(value, **kwargs)
        self.update_keys()

    def update_keys(self):
        pos, name = self.get_configuration()
        update_keys(U_FILTER=name, U_FILTTH=pos)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_filter [-h | --help]
    vampires_filter <slot>
    vampires_filter (status|position)

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
    <slot>          Moves the filter wheel to the given slot, either a number or a filter name
    status          Returns the current filter name
    position        Returns the current filter slot

Configurations:
{configurations}"""


# setp 4. action
def main():
    vampires_filter = connect(PYRO_KEYS["filter"])
    __doc__ = vampires_filter.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    elif args["<slot>"].lower() in ("status", "st"):
        pos = vampires_filter.get_position()
        vampires_filter.update_keys()
        print(VAMPIRESFilter.format_str.format(pos, vampires_filter.status()))
    elif args["<slot>"].lower() in ("position", "pos", "slot"):
        print(vampires_filter.get_position())
        vampires_filter.update_keys()
    elif args["<slot>"]:
        try:
            slot = int(args["<slot>"])
            vampires_filter.move_configuration_idx(slot)
        except ValueError:
            vampires_filter.move_configuration_name(args["<slot>"])


if __name__ == "__main__":
    main()
