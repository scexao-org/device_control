import logging
import re

import click
import rich
from scxconf.pyrokeys import VCAM1, VCAM2
from swmain.network.pyroclient import connect
from swmain.redis import update_keys

from device_control.base import SSHDevice

logger = logging.getLogger(__name__)


class ImageRotator(SSHDevice):
    CONF = "facility/conf_image_rotator.toml"

    KEY_MAP = {"stage angle": "D_IMRANG", "stage angle (pupil, theoretical)": "D_IMRPAD"}

    CAMS_TO_CHECK = (VCAM1, VCAM2)

    def get_status(self):
        status = self.ask_command("imr st")
        lines = status.splitlines()
        status_dict = {}
        for line in lines:
            key, value = re.split(":\s+", line)
            try:
                val = float(value)
            except ValueError:
                val = value
            status_dict[key] = val
        self.update_keys(status_dict)
        return status_dict

    def get_position(self):
        status = self.get_status()
        return status["stage angle"]

    def move_absolute(self, value):
        self.send_command(f"imr ma {value}")

    def move_relative(self, value: float):
        self.send_command(f"imr mr {value}")

    def update_keys(self, status=None):
        if status is None:
            status = self.get_status()
        # normalize status dict
        hdr_dict = {self.KEY_MAP[k]: v for k, v in status.items() if k in self.KEY_MAP}
        update_keys(**hdr_dict)
        ## update cams
        for cam in self.CAMS_TO_CHECK:
            try:
                cam_pyro = connect(cam)
                for key, value in hdr_dict.items():
                    cam_pyro.set_keyword(key, value)
            except Exception:
                logger.exception(f"Unable to push keywords to cam {cam}")


@click.group("imr", help="Simple interface for interacting with the image rotator.")
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)
    ctx.obj["imr"] = ImageRotator.connect()


@main.command("pos")
@click.pass_obj
def posn(obj):
    print(obj["imr"].get_position())


@main.command("status")
@click.pass_obj
def status(obj):
    rich.print(obj["imr"].get_status())


if __name__ == "__main__":
    main()
