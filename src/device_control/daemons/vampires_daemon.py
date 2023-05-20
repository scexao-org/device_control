import os
from argparse import ArgumentParser
from pathlib import Path

from device_control.drivers.conex import CONEXDevice
from device_control.drivers.thorlabs import ThorlabsFlipMount, ThorlabsTC, ThorlabsWheel
from device_control.drivers.zaber import ZaberDevice
from device_control.multi_device import MultiDevice
from device_control.vampires import PYRO_KEYS
from device_control.vampires.vampires_mask_wheel import VAMPIRESMaskWheel
from scxconf import IP_VAMPIRES, PYRONS3_HOST, PYRONS3_PORT
from swmain.network.pyroserver_registerable import PyroServer
from device_control.vampires import VAMPIRESBeamsplitter, VAMPIRESFilter, VAMPIRESQWP, VAMPIRESDiffWheel

parser = ArgumentParser(
    prog="vampires_daemon",
    description="Launch the daemon for the devices controlled by the VAMPIRES computer.",
)

conf_dir = Path(os.getenv("CONF_DIR", f"{os.getenv('HOME')}/src/device_control/conf/"))

## First step, divide into individual functions
def launch_beamsplitter():
    config = conf_dir / "devices/vampires/conf_vampires_beamsplitter.toml"
    beamsplitter = VAMPIRESBeamsplitter.from_config(config)
    return beamsplitter


# def launch_focus():
#     config = conf_dir / "devices/vampires/conf_vampires_focus.toml"
#     focus = CONEXDevice.from_config(config)
#     return focus


# def launch_camfocus():
#     config = conf_dir / "devices/vampires/conf_vampires_camfocus.toml"
#     camfocus = ZaberDevice.from_config(config)
#     return camfocus


def launch_diffwheel():
    config = conf_dir / "devices/vampires/conf_vampires_diffwheel.toml"
    diffwheel = VAMPIRESDiffWheel.from_config(config)
    return diffwheel


# def launch_mask():
#     config = conf_dir / "devices/vampires/conf_vampires_mask.toml"
#     mask = VAMPIRESMaskWheel.from_config(config)
#     return mask


def launch_qwp1():
    config = conf_dir / "devices/vampires/conf_vampires_qwp1.toml"
    qwp1 = VAMPIRESQWP.from_config(config, number=1)
    return qwp1


def launch_qwp2():
    config = conf_dir / "devices/vampires/conf_vampires_qwp2.toml"
    qwp2 = VAMPIRESQWP.from_config(config, number=2)
    return qwp2


def launch_filter():
    config = conf_dir / "devices/vampires/conf_vampires_filter.toml"
    filter = VAMPIRESFilter.from_config(config)
    return filter


# def launch_pupil():
#     config = conf_dir / "devices/vampires/conf_vampires_pupil.toml"
#     pupil = ThorlabsFlipMount.from_config(config)
#     return pupil


# def launch_tc():
#     config = conf_dir / "devices/vampires/conf_vampires_tc.toml"
#     tc = ThorlabsTC.from_config(config)
#     return tc


def main():
    args = parser.parse_args()
    server = PyroServer(bindTo=(IP_VAMPIRES, 0), nsAddress=(PYRONS3_HOST, PYRONS3_PORT))
    ## create device objects
    print("Initializing devices")

    devices = {
        "beamsplitter": launch_beamsplitter(),
        # "focus": launch_focus(),
        # "camfocus": launch_camfocus(),
        "diffwheel": launch_diffwheel(),
        # "mask": launch_mask(),
        "qwp1": launch_qwp1(),
        "qwp2": launch_qwp2(),
        "filter": launch_filter(),
        # "tc": launch_tc(),
        # "pupil": launch_pupil(),
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
