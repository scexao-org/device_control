import argparse
from functools import partial

import click
import Pyro4
from scxconf import IP_VAMPIRES, PYRONS3_HOST, PYRONS3_PORT
from swmain.infra.badsystemd.aux import auto_register_to_watchers
from swmain.network.pyroserver_registerable import PyroServer

from device_control.vampires import (
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

DEVICE_MAP = {
    "bs": partial(VAMPIRESBeamsplitter.connect, local=True),
    "camfocus": partial(VAMPIRESCamFocus.connect, local=True),
    "diff": partial(VAMPIRESDiffWheel.connect, local=True),
    "fieldstop": partial(VAMPIRESFieldstop.connect, local=True),
    "filt": partial(VAMPIRESFilter.connect, local=True),
    "flc": partial(VAMPIRESFLCStage.connect, local=True),
    "focus": partial(VAMPIRESFocus.connect, local=True),
    "mask": partial(VAMPIRESMaskWheel.connect, local=True),
    "mbi": partial(VAMPIRESMBIWheel.connect, local=True),
    "puplens": partial(VAMPIRESPupilLens.connect, local=True),
    "tc": partial(VAMPIRESTC.connect, local=True),
    "trig": partial(VAMPIRESTrigger.connect, local=True),
}

parser = argparse.ArgumentParser(
    "vampires_devices",
    description="Launch the daemon for the devices controlled by the VAMPIRES computer.",
)

Pyro4.config.SERVERTYPE = "thread"  # Override from multiplex default.


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
        except Exception:
            click.secho(f" ! Failed to connect {key.upper()}", bg=(114, 24, 23), fg=(224, 224, 226))

    click.echo("\nThe following variables are available in the shell:")
    click.secho(", ".join(available), bold=True)
    ## Start server
    server.start()


if __name__ == "__main__":
    main()
