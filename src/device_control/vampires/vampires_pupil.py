import sys

from docopt import docopt

from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.
from device_control.drivers import ThorlabsFlipMount
from swmain.redis import update_keys


class VAMPIRESPupilLens(ThorlabsFlipMount):
    def _update_keys(self, position):
        update_keys(U_PUPIL=position.upper())

    def help_message(self):
        return f"""Usage:
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
    vampires_pupil = connect(PYRO_KEYS["pupil"])
    __doc__ = vampires_pupil.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif args["<pos>"].lower() in ("status", "st"):
        if vampires_pupil.configurations:
            print("{}: {}".format(vampires_pupil.get_configuration()))
        else:
            print(vampires_pupil.get_position())
    elif args["<pos>"]:
        vampires_pupil.set_position(args["<pos>"])
    vampires_pupil.update_keys()


if __name__ == "__main__":
    main()