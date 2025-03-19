import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VAMPIRES
from swmain.redis import update_keys

from device_control.multi_device import MultiDevice


class VAMPIRESFocus(MultiDevice):
    CONF = "vampires/conf_vampires_focus.toml"
    PYRO_KEY = VAMPIRES.FOCUS
    format_str = "{0}: {1:10s} {{lens={2:5.02f} mm, cam={2:5.02f} mm}}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices["lens"]._update_keys = lambda p: update_keys(U_FCSF=p)
        self.devices["cam"]._update_keys = lambda p: update_keys(U_CAMFCF=p)

    def _update_keys(self, positions):
        _, name = self.get_configuration(positions=positions)
        update_keys(U_FCS=name, U_CAMFCS=name)

    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value']['lens'], c['value']['cam'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vampires_focus [-h | --help]
    vampires_focus status
    vampires_focus lens (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_focus cam  (status|position|home|goto|nudge|stop|reset) [<pos>]
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
    posns = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif len(sys.argv) == 2 and args["status"]:
        posns, status = vampires_focus.get_status()
        print(status)
        vampires_focus.update_keys(posns)
        return
    elif args["lens"]:
        substage = "lens"
    elif args["cam"]:
        substage = "cam"
    elif args["<configuration>"]:
        if args["--save"]:
            try:
                config_idx = int(args["<configuration>"])
            except ValueError:
                config_idx = vampires_focus.get_config_index_from_name(args["<configuration>"])
            vampires_focus.save_configuration(index=config_idx)
        else:
            vampires_focus.move_configuration(args["<configuration>"])
    if args["status"] or args["position"]:
        print(vampires_focus.get_position(substage))
    elif args["home"]:
        vampires_focus.home(substage)
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        vampires_focus.move_absolute(substage, new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_focus.move_relative(substage, rel_pos)
    elif args["stop"]:
        vampires_focus.stop(substage)
    elif args["reset"]:
        substage.reset()
    vampires_focus.update_keys(posns)


if __name__ == "__main__":
    main()
