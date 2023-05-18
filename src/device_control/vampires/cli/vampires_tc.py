import sys

from docopt import docopt

from device_control.vampires import PYRO_KEYS
from swmain.network.pyroclient import (
    connect,
)  # Requires scxconf and will fetch the IP addresses there.

vampires_tc = connect(PYRO_KEYS["tc"])

__doc__ = f"""Usage:
    vampires_tc [-h | --help]
    vampires_tc <temp>
    vampires_tc (status|temp|enable|disable)

Options:
    -h, --help   Show this screen

Stage commands:
    <temp>       Sets the target temperature (in °C)
    temp         Returns the target temperature (in °C)
    status       Returns the temperature controller status
    enable       Enables the temperature controller PID loop
    disable      Disables the temperature controller PID loop"""

# setp 4. action
def main():
    args = docopt(__doc__, options_first=True)
    if len(sys.argv) == 1:
        print(__doc__)
    elif args["<temp>"].lower() in ("status", "st"):
        stat_dict = vampires_tc.status()
        enabled_str = "Enabled" if stat_dict["enabled"] else "Disabled"
        print(
            f"{enabled_str}: Tact = {vampires_tc.temp:4.01f}°C / Tset = {vampires_tc.target:4.01f}°C"
        )
    elif args["<temp>"].lower() in ("temp"):
        print(vampires_tc.temp)
    elif args["<temp>"].lower() in ("enable", "en"):
        vampires_tc.enable()
    elif args["<temp>"].lower() in ("disable", "dis"):
        vampires_tc.disable()
    elif args["<temp>"]:
        vampires_tc.target = float(args["<temp>"])


if __name__ == "__main__":
    main()
