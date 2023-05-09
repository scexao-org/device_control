from docopt import docopt
import sys

from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from device_control.vampires import PYRO_KEYS

vampires_pupil = connect(PYRO_KEYS["pupil"])


__doc__ = f"""Usage:
    vampires_pupil [-h | --help]
    vampires_pupil <pos>
    vampires_pupil status

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands
    <pos>        Move the mount 'in' or 'out'

Stage commands:
    status       Returns the current mount position"""

# setp 4. action
def main():
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    elif args["<pos>"].lower() in ("status", "st"):
        if vampires_pupil.configurations:
            print("{}: {}".format(vampires_pupil.get_configuration()))
        else:
            print(vampires_pupil.position)
    elif args["<pos>"]:
        vampires_pupil.flip(args["<pos>"])


if __name__ == "__main__":
    main()
