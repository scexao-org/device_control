from argparse import ArgumentParser

from device_control.vampires import (
    VAMPIRESQWP,
    VAMPIRESTC,
    VAMPIRESBeamsplitter,
    VAMPIRESCamFocus,
    VAMPIRESDiffWheel,
    VAMPIRESFieldstop,
    VAMPIRESFilter,
    VAMPIRESFLCStage,
    VAMPIRESFocus,
    VAMPIRESMaskWheel,
    VAMPIRESMBIWheel,
    VAMPIRESPupilLens,
    VAMPIRESTrigger,
)

from scxconf import IP_VAMPIRES, PYRONS3_HOST, PYRONS3_PORT
from swmain.network.pyroserver_registerable import PyroServer

parser = ArgumentParser(
    prog="vampires_devices",
    description="Launch the daemon for the devices controlled by the VAMPIRES computer.",
)


def main():
    parser.parse_args()
    server = PyroServer(bindTo=(IP_VAMPIRES, 0), nsAddress=(PYRONS3_HOST, PYRONS3_PORT))
    ## create device objects
    print("Initializing devices")

    devices = {
        "bs": VAMPIRESBeamsplitter.connect(local=True),
        "focus": VAMPIRESFocus.connect(local=True),
        "camfocus": VAMPIRESCamFocus.connect(local=True),
        "flc": VAMPIRESFLCStage.connect(local=True),
        # "diffwheel": VAMPIRESDiffWheel.connect(local=True),
        "mask": VAMPIRESMaskWheel.connect(local=True),
        "mbi": VAMPIRESMBIWheel.connect(local=True),
        "qwp1": VAMPIRESQWP.connect(1, local=True),
        "qwp2": VAMPIRESQWP.connect(2, local=True),
        "filt": VAMPIRESFilter.connect(local=True),
        # "fieldstop": VAMPIRESFieldstop.connect(local=True),
        "tc": VAMPIRESTC.connect(local=True),
        # "trigger": VAMPIRESTrigger.connect(local=True),
        "pupil": VAMPIRESPupilLens.connect(local=True),
    }
    ## Add to Pyro server
    print("Adding devices to pyro", end="\n  ")
    for key, device in devices.items():
        print(f"{key}: {device.PYRO_KEY}", end="\n  ")
        globals()[key] = device
        server.add_device(device, device.PYRO_KEY, add_oneway_callables=True)
    print()
    print(f"the following variables are available in the shell:\n{', '.join(devices.keys())}")
    ## Start server
    server.start()


if __name__ == "__main__":
    main()
