import os
import sys

from docopt import docopt

from device_control import conf_dir
from device_control.drivers import ZaberDevice
from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (  # Requires scxconf and will fetch the IP addresses there.
    connect,
)
from swmain.redis import update_keys


class VAMPIRESFLCStage(ZaberDevice):
    format_str = "{0}: {1:10s} {{{2:5.02f} mm}}"

    def _update_keys(self, position):
        _, name = self.get_configuration(position=position)
        update_keys(U_FLCST=name.upper(), U_FLCSTP=position)

    def help_message(self):
        configurations = "\n".join(
            f"    {VAMPIRESFLCStage.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_focus [-h | --help]
    vampires_focus [-w | --wait] (status|position|home|goto|nudge|stop|reset) [<pos>]

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
    status          Returns the current status of the FLC stage
    position        Returns the current position of the FLC stage, in mm
    home            Homes the FLC stage
    goto  <pos>     Move the FLC stage to the given position, in mm
    nudge <pos>     Move the FLC stage relatively by the given position, in mm
    stop            Stop the FLC stage
    reset           Reset the FLC stage
    
Configurations:
{configurations}"""


# setp 4. action
def main():
    if os.getenv("WHICHCOMP") == "V":
        vampires_flc = VAMPIRESFLCStage.from_config(
            conf_dir / "vampires" / "conf_vampires_flc.toml"
        )
    else:
        vampires_flc = connect(PYRO_KEYS["flc"])
    __doc__ = vampires_flc.help_message()
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        posn = vampires_flc.get_position()
        idx, name = vampires_flc.get_configuration(posn)
        print(VAMPIRESFLCStage.format_str.format(idx, name, posn))
    elif args["position"]:
        print(vampires_flc.get_position())
    elif args["home"]:
        vampires_flc.home()
    elif args["goto"]:
        pos = float(args["<pos>"])
        vampires_flc.move_absolute(pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_flc.move_relative(rel_pos)
    elif args["stop"]:
        vampires_flc.stop()
    elif args["reset"]:
        vampires_flc.reset()
    vampires_flc.update_keys()


if __name__ == "__main__":
    main()
