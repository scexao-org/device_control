import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VAMPIRES
from swmain.redis import update_keys

from device_control.drivers import ThorlabsFlipMount


class VAMPIRESPupilLens(ThorlabsFlipMount):
    CONF = "vampires/conf_vampires_pupil.toml"
    PYRO_KEY = VAMPIRES.PUPIL
    format_str = "{0}: {1}"

    def _update_keys(self, position):
        _, state = self.get_configuration(position)
        update_keys(U_PUPST=state.upper())

    def help_message(self):
        return """Usage:
    vampires_pupil [-h | --help]
    vampires_pupil status
    vampires_pupil <pos>

Options:
    -h, --help   Show this screen
    <pos>        Move the mount 'in' or 'out'

Stage commands:
    status       Returns the current mount position"""


# setp 4. action
def main():
    vampires_pupil = VAMPIRESPupilLens.connect(os.getenv("WHICHCOMP") == "V")
    __doc__ = vampires_pupil.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif args["status"]:
        posn, status = vampires_pupil.get_status()
        print(status)
    elif args["<pos>"]:
        vampires_pupil.move_configuration_name(args["<pos>"])
    vampires_pupil.update_keys(posn)


if __name__ == "__main__":
    main()
