import argparse
from functools import partial

import click
from scxconf import IP_AORTS_SUMMIT, PYRONS3_HOST, PYRONS3_PORT
<<<<<<< HEAD
from swmain.network.pyroserver_registerable import PyroServer

from device_control.viswfs import (
    VISWFSCamFocus,
    VISWFSFlipMount1,
    VISWFSFlipMount2,
    VISWFSPickoffBS,
    VISWFSRotStage1,
    VISWFSRotStage2,
    VISWFSTrombone1,
    VISWFSTrombone2,
)
=======

from device_control.viswfs import (
    VISWFSPickoffBS,
    VISWFSCamFocus,
    VISWFSTrombone1,
    VISWFSTrombone2,
    VISWFSRotStage1,
    VISWFSRotStage2,
    VISWFSFlipMount1,
    VISWFSFlipMount2,
)
from swmain.network.pyroserver_registerable import PyroServer
>>>>>>> adding device control for nlCWFS

DEVICE_MAP = {
    "pickoff": partial(VISWFSPickoffBS.connect, local=True),
    "camfocus": partial(VISWFSCamFocus.connect, local=True),
    "trombone1": partial(VISWFSTrombone1.connect, local=True),
    "trombone2": partial(VISWFSTrombone2.connect, local=True),
    "rs1": partial(VISWFSRotStage1.connect, local=True),
    "rs2": partial(VISWFSRotStage2.connect, local=True),
    "flipmount1": partial(VISWFSFlipMount1.connect, local=True),
    "flipmount2": partial(VISWFSFlipMount2.connect, local=True),
}

parser = argparse.ArgumentParser(
    "viswfs_devices",
    description="Launch the daemon for the devices controlled by the AORTS computer.",
)


def main():
    parser.parse_args()
    server = PyroServer(bindTo=(IP_AORTS_SUMMIT, 0), nsAddress=(PYRONS3_HOST, PYRONS3_PORT))
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
<<<<<<< HEAD
        except Exception:
=======
        except:
>>>>>>> adding device control for nlCWFS
            click.secho(
                f" ! Failed to connect {key} : {device.PYRO_KEY}",
                bg=(114, 24, 23),
                fg=(224, 224, 226),
            )

<<<<<<< HEAD
    click.echo("\nThe following variables are available in the shell:")
=======
    click.echo(f"\nThe following variables are available in the shell:")
>>>>>>> adding device control for nlCWFS
    click.secho(", ".join(available), bold=True)
    ## Start server
    server.start()


if __name__ == "__main__":
    main()
