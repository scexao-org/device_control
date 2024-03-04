from __future__ import annotations

import typing as typ

import os
import sys

from docopt import docopt
from scxconf.pyrokeys import SCEXAO
from swmain.redis import update_keys


from device_control.multi_device import MultiDevice


class GLINTSteeringX(MultiDevice):
    '''
    Beware: this class used for steering 1 AND steering 2
    Class attributes to be set in connect overload
    '''
    # CONF = None
    # PYRO_KEY = None
    format_str = "{0:2d}: {1:6.2f} deg {{th={2:6.2f} deg}}"

        
    def _update_keys(self, posn):
        ...
        #update_keys(X_POLARP=posn)

    def help_message(self) -> str:
        configurations = "\n".join(
            f"    {self.format_str.format(c['idx'], c['name'], c['value']['x'], c['value']['y'], c['value']['f'])}"
            for c in self.configurations
        )
        return f"""
GLINT Conex AGAP control. X = 1 or 2 for either stage.

Usage:
    glint_steeringX [-h | --help]
    glint_steeringX status
    glint_steeringX u (status|target|goto|nudge|stop|reset) [<pos>]
    glint_steeringX v (status|target|goto|nudge|stop|reset) [<pos>]
    glint_steeringX <configuration>

Options:
    -h, --help   Show this screen

Stage commands:
    status          Returns the current position of the stage
    target          Returns the target position of the stage
    goto  <pos>     Move the stage to the given angle
    nudge <pos>     Move the stage relatively by the given angle
    stop            Stop the stage
    reset           Reset the stage

Configurations:
{configurations}"""


    @classmethod
    def connect(cls, index: int, local=False, filename=None, pyro_key=None):
        cls.PYRO_KEY = f"GLINT_STEER_{index}" # FIXME WHEN PYRO
        cls.CONF = f"glint/conf_glint_steering{index}.toml"
        return super().connect(local, filename, pyro_key)


# step 4. action
def main(index: int):
    glint_steering = GLINTSteeringX.connect(index, os.getenv("WHICHCOMP") == "5")

    _doc = glint_steering.help_message()
    args = docopt(_doc, options_first=True)

    posns = None
    if len(sys.argv) == 1:
        print(_doc)
        return
    elif len(sys.argv) == 2 and args["status"]:
        posns, status = glint_steering.get_status()
        print(status)
        glint_steering.update_keys(posns)
        return
    elif args["u"]:
        substage = "u"
    elif args["v"]:
        substage = "v"

    elif args["<configuration>"]:
        index = args["<configuration>"]
        return glint_steering.move_configuration(index)

    if args["status"]:
        print(glint_steering.get_position(substage))
    elif args["goto"]:
        new_pos = float(args["<pos>"])
        glint_steering.move_absolute(substage, new_pos)
    elif args["nudge"]:
        rel_pos = float(args["<pos>"])
        glint_steering.move_relative(substage, rel_pos)
    elif args["stop"]:
        glint_steering.stop(substage)
    elif args["reset"]:
        glint_steering.reset(substage)
    glint_steering.update_keys(posns)

def main1():
    return main(1)

def main2():
    return main(2)

if __name__ == "__main__":
    
    if len(sys.argv) < 1 or sys.argv[0] in ('1', '2'):
        raise ValueError('First argument to steering.py must be "1" or "2" to dispatch to GLINT steering 1 or steering 2.')
    index = int(sys.argv[0]) # Parse stage index.
    sys.argv = sys.argv[1:] # Bump one arg out.
    main(index)
