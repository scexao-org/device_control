import os
import sys

from docopt import docopt
from scxconf.pyrokeys import VAMPIRES

from device_control import conf_dir
from device_control.drivers import CONEXDevice
from device_control.vampires.cameras import connect_cameras
from swmain.redis import update_keys


class VAMPIRESQWP(CONEXDevice):
    CONF = "vampires/conf_vampires_qwp{0:d}.toml"
    format_str = "QWP{0:1d}: {1:6.02f}"

    def __init__(self, number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if number == 1:
            self.PYRO_KEY = VAMPIRES.QWP1
        elif number == 2:
            self.PYRO_KEY = VAMPIRES.QWP2
        else:
            raise ValueError(f"Invalid QWP number: {number}")
        self.number = number
        self.cams = connect_cameras()

    def _config_extras(self):
        return {"number": self.number}

    def _update_keys(self, theta):
        kwargs = {
            f"U_QWP{self.number:1d}": theta,
            f"U_QWP{self.number:1d}TH": theta - self.offset,
        }
        update_keys(**kwargs)
        for cam in self.cams:
            if cam is not None:
                cam.set_keyword(f"U_QWP{self.number:1d}", theta)
                cam.set_keyword(f"U_QWP{self.number:1d}TH", theta - self.offset)

    def _move_absolute(self, value: float, wait=True):
        return super()._move_absolute(value % 360, wait)

    @classmethod
    def connect(__cls__, num: int, local=False):
        filename = conf_dir / __cls__.CONF.format(num)
        if num == 1:
            pyro_key = VAMPIRES.QWP1
        elif num == 2:
            pyro_key = VAMPIRES.QWP2
        else:
            raise ValueError(f"Invalid QWP number: {num}")
        return super().connect(local, filename=filename, pyro_key=pyro_key)

    def get_status(self):
        posn = self.get_position()
        output = self.format_str.format(self.number, posn)
        return posn, output


__doc__ = f"""Usage:
    vampires_qwp [-h | --help]
    vampires_qwp status
    vampires_qwp 1 (status|position|home|goto|nudge|stop|reset) [<pos>]
    vampires_qwp 2 (status|position|home|goto|nudge|stop|reset) [<pos>]

Options:
    -h, --help   Show this screen
    -w, --wait   Block command until position has been reached, for applicable commands

Stage commands:
    status          Returns the current status of the QWP wheel
    position        Returns the current position of the QWP wheel, in deg
    home            Homes the stage
    goto  <pos>     Move the stage to the given angle
    nudge <pos>     Move the stage relatively by the given angle
    stop            Stop the stage
    reset           Reset the stage"""


# setp 4. action
def main():
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
        return
    local = os.getenv("WHICHCOMP") == "V"
    if args["1"]:
        vampires_qwp = VAMPIRESQWP.connect(1, local=local)
    elif args["2"]:
        vampires_qwp = VAMPIRESQWP.connect(2, local=local)
    elif args["status"]:
        for cam in (1, 2):
            qwp = VAMPIRESQWP.connect(cam, local=local)
            posn = qwp.get_position()
            qwp.update_keys(posn)
            print(qwp.format_str.format(cam, posn))
        return

    posn = None
    if args["status"]:
        posn, status = vampires_qwp.get_status()
        print(status)
    elif args["position"]:
        posn = vampires_qwp.get_position()
        print(posn)
    elif args["home"]:
        vampires_qwp.home()
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        vampires_qwp.move_absolute(new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        vampires_qwp.move_relative(rel_pos)
    elif args["stop"]:
        vampires_qwp.stop()
    elif args["reset"]:
        vampires_qwp.reset()
    vampires_qwp.update_keys(posn)


if __name__ == "__main__":
    main()
