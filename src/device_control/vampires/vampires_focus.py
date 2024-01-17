import os
import sys

from device_control.drivers import CONEXDevice
from docopt import docopt
from scxconf.pyrokeys import VAMPIRES
from swmain.redis import update_keys


class VAMPIRESFocus(CONEXDevice):
    CONF = "vampires/conf_vampires_focus.toml"
    PYRO_KEY = VAMPIRES.FOCUS
    format_str = "{0}: {1:10s} {{{2:5.02f} mm}}"

    def _update_keys(self, position):
        _, name = self.get_configuration(position=position)
        update_keys(U_FCS=name, U_FCSF=position)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_focus [-h | --help]
    vampires_focus (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_focus [--save] <configuration>

Options:
    -h, --help   Show this screen
    --save       Save the current position to the given configuration

Stage commands:
    status          Returns the current status of the focus stage
    position        Returns the current position of the focus stage, in mm
    home            Homes the focus stage
    goto  <pos>     Move the focus stage to the given position, in mm
    nudge <pos>     Move the focus stage relatively by the given position, in mm
    stop            Stop the focus stage
    reset           Reset the focus stage
    
Configurations:
{configurations}"""


# setp 4. action
def main():
    vampires_focus = VAMPIRESFocus.connect(os.getenv("WHICHCOMP") == "V")
    __doc__ = vampires_focus.help_message()
    args = docopt(__doc__, options_first=True)
    posn = None
    if len(sys.argv) == 1:
        print(__doc__)
    if args["status"]:
        posn, status = vampires_focus.get_status()
        print(status)
    elif args["position"]:
        posn = vampires_focus.get_position()
        print(posn)
    elif args["home"]:
        vampires_focus.home()
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        vampires_focus.move_absolute(new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_focus.move_relative(rel_pos)
    elif args["stop"]:
        vampires_focus.stop()
    elif args["reset"]:
        vampires_focus.reset()
    elif args["<configuration>"]:
        if args["--save"]:
            try:
                config_idx = int(args["<configuration>"])
            except ValueError:
                config_idx = vampires_focus.get_config_index_from_name(args["<configuration>"])
            vampires_focus.save_configuration(index=config_idx)
        else:
            vampires_focus.move_configuration(args["<configuration>"])
    vampires_focus.update_keys(posn)


if __name__ == "__main__":
    main()
