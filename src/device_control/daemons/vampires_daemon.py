import os
from argparse import ArgumentParser
from pathlib import Path

from device_control.vampires import PYRO_KEYS
from scxconf import IP_VAMPIRES, PYRONS3_HOST, PYRONS3_PORT
from swmain.network.pyroserver_registerable import PyroServer
from device_control.vampires import *

parser = ArgumentParser(
    prog="vampires_daemon",
    description="Launch the daemon for the devices controlled by the VAMPIRES computer.",
)

conf_dir = Path(os.getenv("CONF_DIR", f"{os.getenv('HOME')}/src/device_control/conf/"))


def main():
    args = parser.parse_args()
    server = PyroServer(bindTo=(IP_VAMPIRES, 0), nsAddress=(PYRONS3_HOST, PYRONS3_PORT))
    ## create device objects
    print("Initializing devices")

    devices = {
        "beamsplitter": VAMPIRESBeamsplitter.from_config(
            conf_dir / "devices/vampires/conf_vampires_beamsplitter.toml"
        ),
        "focus": VAMPIRESFocus.from_config(
            conf_dir / "devices/vampires/conf_vampires_focus.toml"
        ),
        "camfocus": VAMPIRESCamFocus.from_config(
            conf_dir / "devices/vampires/conf_vampires_camfocus.toml"
        ),
        # "flc":  VAMPIRESFLCStage.from_config(conf_dir / "devices/vampires/conf_vampires_flcß.toml"),
        "diffwheel": VAMPIRESDiffWheel.from_config(
            conf_dir / "devices/vampires/conf_vampires_diffwheel.toml"
        ),
        "mask": VAMPIRESMaskWheel.from_config(
            conf_dir / "devices/vampires/conf_vampires_mask.toml"
        ),
        # "mbi":  VAMPIRESMBIWheel.from_config(conf_dir / "devices/vampires/conf_vampires_mbi.toml"),
        "qwp1": VAMPIRESQWP.from_config(
            conf_dir / "devices/vampires/conf_vampires_qwp1.toml", number=1
        ),
        "qwp2": VAMPIRESQWP.from_config(
            conf_dir / "devices/vampires/conf_vampires_qwp2.toml", number=2
        ),
        "filter": VAMPIRESFilter.from_config(
            conf_dir / "devices/vampires/conf_vampires_filter.toml"
        ),
        "tc": VAMPIRESTC.from_config(
            conf_dir / "devices/vampires/conf_vampires_tc.toml"
        ),
        # "pupil": VAMPIRESPupilLens.from_config(conf_dir / "devices/vampires/conf_vampires_pupil.toml"),
    }
    ## Add to Pyro server
    print("Adding devices to pyro", end="\n  ")
    for key, device in devices.items():
        print(f"{key}: {PYRO_KEYS[key]}", end="\n  ")
        globals()[key] = device
        server.add_device(device, PYRO_KEYS[key], add_oneway_callables=True)
    print()
    print(
        f"the following variables are available in the shell:\n{', '.join(devices.keys())}"
    )
    ## Start server
    server.start()


if __name__ == "__main__":
    main()
