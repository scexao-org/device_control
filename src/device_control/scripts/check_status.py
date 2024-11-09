import click
from scxconf import pyrokeys as pk
from swmain.network.pyroclient import connect


def check_connection(device_name: str):
    try:
        print(f"Checking {device_name}")
        print(f"Checking {device_name}")
        connect(device_name)
    except Exception:
        return False
    return True


def check_needs_homed(device_name: str, sub=None) -> bool:
    device = connect(device_name)
    if sub is not None:
        return device.needs_homing(sub)
    return device.needs_homing()


ALL_CONEX_DEVICES = [
    (pk.VAMPIRES.BS, None),
    (pk.VAMPIRES.DIFF, None),
    (pk.VAMPIRES.FOCUS, None),
    (pk.VAMPIRES.FIELDSTOP, "f"),
    (pk.VAMPIRES.FIELDSTOP, "x"),
    (pk.VAMPIRES.FIELDSTOP, "y"),
    (pk.VAMPIRES.MASK, "theta"),
    (pk.VAMPIRES.MBI, None),
    (pk.VAMPIRES.QWP1, None),
    (pk.VAMPIRES.QWP2, None),
    (pk.SCEXAO.POL, None),
    # (pk.VISWFS.RS1, None),
    # (pk.VISWFS.RS2, None),
]


@click.command("check_devices")
def check_devices(device_list=ALL_CONEX_DEVICES):
    for device in device_list:
        is_connected = check_connection(device[0])
        if not is_connected:
            click.secho(f"{device[0]} is not connected to PyRO server", bg="blue", fg="black")
            continue
        needs_homed = check_needs_homed(*device)
        if needs_homed:
            device_name = device[0]
            if device[1] is not None:
                device_name += device[1]
            click.secho(f"{device_name} needs homed!", bg="red", fg="black")
    click.echo("Finished checking devices")


if __name__ == "__main__":
    check_devices()
