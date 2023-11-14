import argparse
from functools import partial

import click
from scxconf import IP_VAMPIRES, PYRONS3_HOST, PYRONS3_PORT

from device_control.vampires import (VAMPIRESQWP, VAMPIRESTC,
                                     VAMPIRESBeamsplitter, VAMPIRESCamFocus,
                                     VAMPIRESDiffWheel, VAMPIRESFilter,
                                     VAMPIRESFLCStage, VAMPIRESFocus,
                                     VAMPIRESMaskWheel, VAMPIRESMBIWheel,
                                     VAMPIRESPupilLens, VAMPIRESTrigger)
from swmain.infra.badsystemd.aux import auto_register_to_watchers
from swmain.network.pyroserver_registerable import PyroServer

DEVICE_MAP = {
    "bs": partial(VAMPIRESBeamsplitter.connect, local=True),
    "focus": partial(VAMPIRESFocus.connect, local=True),
    "camfocus": partial(VAMPIRESCamFocus.connect, local=True),
    "flc": partial(VAMPIRESFLCStage.connect, local=True),
    "diff": partial(VAMPIRESDiffWheel.connect, local=True),
    "mask": partial(VAMPIRESMaskWheel.connect, local=True),
    "mbi": partial(VAMPIRESMBIWheel.connect, local=True),
    "qwp1": partial(VAMPIRESQWP.connect, 1, local=True),
    "qwp2": partial(VAMPIRESQWP.connect, 2, local=True),
    "filt": partial(VAMPIRESFilter.connect, local=True),
    "tc": partial(VAMPIRESTC.connect, local=True),
    "trig": partial(VAMPIRESTrigger.connect, local=True),
    "puplens": partial(VAMPIRESPupilLens.connect, local=True),
}

parser = argparse.ArgumentParser(
    "vampires_devices",
    description="Launch the daemon for the devices controlled by the VAMPIRES computer.",
)


def main():
    parser.parse_args()
    auto_register_to_watchers("VAMP_PYRO", "VAMPIRES PyRO devices")
    server = PyroServer(bindTo=(IP_VAMPIRES, 0), nsAddress=(PYRONS3_HOST, PYRONS3_PORT))
    ## create device objects
    click.echo("Initializing devices")
    available = []
    for key, connect_func in DEVICE_MAP.items():
        try:
            device = connect_func()
            ## Add to Pyro server
            click.echo(f" - {key}: {device.PYRO_KEY}")
            globals()[key] = device
            server.add_device(device, device.PYRO_KEY, add_oneway_callables=True)
            available.append(key)
        except:
            click.secho(
                f" ! Failed to connect {key} : {device.PYRO_KEY}",
                bg=(114, 24, 23),
                fg=(224, 224, 226),
            )

    click.echo(f"\nThe following variables are available in the shell:")
    click.secho(", ".join(available), bold=True)
    ## Start server
    server.start()


if __name__ == "__main__":
    main()
