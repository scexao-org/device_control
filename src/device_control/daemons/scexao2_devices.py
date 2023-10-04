from argparse import ArgumentParser
from functools import partial

import click
from scxconf import IP_SC2, PYRONS3_HOST, PYRONS3_PORT

from device_control.scexao import SCExAOPolarizer
from device_control.vampires import VAMPIRESFieldstop
from swmain.network.pyroserver_registerable import PyroServer

parser = ArgumentParser(
    prog="scexao2_devices",
    description="Launch the daemon for the devices controlled by the scexao2 computer.",
)

DEVICE_MAP = {
    "vampires_fieldstop": partial(VAMPIRESFieldstop.connect, local=True),
    "polarizer": partial(VAMPIRESFieldstop.connect, local=True),
}


def main():
    parser.parse_args()
    server = PyroServer(bindTo=(IP_SC2, 0), nsAddress=(PYRONS3_HOST, PYRONS3_PORT))
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
