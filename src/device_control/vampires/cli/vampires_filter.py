import sys

from docopt import docopt

from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.

vampires_filter = connect(PYRO_KEYS["filter"])

format_str = "{0:1d}: {1:8s}"
configurations = "\n".join(
    f"    {format_str.format(c['idx'], c['name'])}"
    for c in vampires_filter.configurations
)

__doc__ = f"""Usage:
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
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    elif args["<slot>"].lower() in ("status", "st"):
        pos = vampires_filter.position()
        print(format_str.format(pos, vampires_filter.status()))
    elif args["<slot>"].lower() in ("position", "pos", "slot"):
        print(vampires_filter.position())
    elif args["<slot>"]:
        try:
            slot = int(args["<slot>"])
            vampires_filter.move_configuration_idx(slot)
        except ValueError:
            vampires_filter.move_configuration_name(args["<slot>"])


if __name__ == "__main__":
    main()
