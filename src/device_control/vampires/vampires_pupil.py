from docopt import docopt
import sys

from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

vampires_pupil = connect(PYRO_KEYS["pupil"])


__doc__ = f"""Usage:
    vampires_filter [-h | --help]
    vampires_filter <pos>
    vampires_filter status

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
    <pos>        Move the mount 'in' or 'out'
    status       Returns the current mount position"""

# setp 4. action
def main():
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    elif args["<pos>"].lower() in ("status", "st"):
        print(vampires_pupil.status())
    elif args["<pos>"]:
        vampires_pupil.flip(args["<pos>"])

if __name__ == "__main__":
    main()
