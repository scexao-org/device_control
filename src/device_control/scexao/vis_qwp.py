import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VAMPIRES
from swmain.redis import update_keys

from device_control import conf_dir
from device_control.multi_device import MultiDevice
from device_control.drivers.thorlabs import ThorlabsElliptec
from device_control.vampires.cameras import connect_cameras


def _update_qwp(qwp, position):
    {
        f"U_QWP{qwp_num:1d}"
    }

class VISQWP(MultiDevice):
    CONF = "scexao/conf_vis_qwp.toml"
    format_str = "{0}: {1:10s} {{QWP1={2:5.02f}°, QWP2={3:5.02f}°}}"
    PYRO_KEY = "SCEXAO_QWP"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices["1"]._update_keys = lambda p: update_keys(U_QWP1=p, U_QWP1TH=p - self.devices["1"].offset)
        self.devices["2"]._update_keys = lambda p: update_keys(U_QWP2=p, U_QWP2TH=p - self.devices["2"].offset)


    def _update_keys(self, positions):
        _, name = self.get_configuration(positions=positions)
        
        
        # kwargs = {f"U_QWP{self.number:1d}": theta, f"U_QWP{self.number:1d}TH": theta - self.offset}
        # update_keys(**kwargs)
        # for cam in connect_cameras():
        #     if cam is not None:
        #         cam.set_keyword(f"U_QWP{self.number:1d}", theta)
        #         cam.set_keyword(f"U_QWP{self.number:1d}TH", theta - self.offset)


    def help_message(self):
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value']['1'], c['value']['2'])}"
            for c in self.configurations
        )
        return f"""Usage:
    vis_qwp [-h | --help]
    vis_qwp (status|home|stop)
    vis_qwp [--save] <configuration>
    vis_qwp 1 (status|position|home|goto|nudge|stop|reset|cont) [<pos>]
    vis_qwp 2 (status|position|home|goto|nudge|stop|reset|cont) [<pos>]

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
    status          Returns the current status of the QWP wheel
    position        Returns the current position of the QWP wheel, in deg
    home            Homes the stage
    goto  <pos>     Move the stage to the given angle, in deg
    nudge <pos>     Move the stage relatively by the given angle, in deg
    cont            Move the stage continuously at maximum speed
    stop            Stop the stage
    reset           Reset the stage
    
Configurations:
{configurations}"""


# setp 4. action
def main():
    # local = os.getenv("WHICHCOMP") == "2"
    local = True
    vis_qwp = VISQWP.connect(local=local)
    __doc__ = vis_qwp.help_message()
    args = docopt(__doc__, options_first=True)
    posns = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if len(sys.argv) == 1:
        print(__doc__)
        return
    elif len(sys.argv) == 2 and args["status"]:
        posns, status = vis_qwp.get_status()
        print(status)
        return
    elif len(sys.argv) == 2 and args["home"]:
        vis_qwp.home_all()
        return
    elif len(sys.argv) == 2 and args["stop"]:
        vis_qwp.stop_all()
        return
    elif args["1"]:
        substage = "1"
    elif args["2"]:
        substage = "2"
    elif args["<configuration>"]:
        if args["--save"]:
            try:
                config_idx = int(args["<configuration>"])
            except ValueError:
                config_idx = vis_qwp.get_config_index_from_name(args["<configuration>"])
            vis_qwp.save_configuration(index=config_idx)
        else:
            vis_qwp.move_configuration(args["<configuration>"])
    if args["status"] or args["position"]:
        print(vis_qwp.get_position(substage))
    elif args["home"]:
        vis_qwp.home(substage)
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        vis_qwp.move_absolute(substage, new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vis_qwp.move_relative(substage, rel_pos)
    elif args["stop"]:
        vis_qwp.stop(substage)
    elif args["reset"]:
        substage.reset()
    vis_qwp.update_keys(posns)


if __name__ == "__main__":
    main()
