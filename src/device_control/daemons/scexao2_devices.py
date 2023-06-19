from argparse import ArgumentParser

from device_control.vampires import VAMPIRESFieldstop
from scxconf import IP_SC2, PYRONS3_HOST, PYRONS3_PORT
from swmain.network.pyroserver_registerable import PyroServer

parser = ArgumentParser(
    prog="scexao2_devices",
    description="Launch the daemon for the devices controlled by the scexao2 computer.",
)


def main():
    parser.parse_args()
    server = PyroServer(bindTo=(IP_SC2, 0), nsAddress=(PYRONS3_HOST, PYRONS3_PORT))
    ## create device objects
    print("Initializing devices")

    devices = {
        "vampires_fieldstop": VAMPIRESFieldstop.connect(local=True),
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
