import sys

from device_control.drivers import CONEXDevice
from docopt import docopt


class AGAPTest(CONEXDevice):
    CONF = "scexao/conf_conex_agap_test.toml"
    PYRO_KEY = ""
    format_str = "{0:2d}: {1:6.2f} deg {{th={2:6.2f} deg}}"

    def _update_keys(self, posn):
        pass

    def move_absolute(self, value, **kwargs):
        return super().move_absolute(value % 360, **kwargs)

    def help_message(self):
        return """Usage:
    TEST unclear
"""


# setp 4. action
def main():
    scexao_pol = AGAPTest.connect(local=True)
    __doc__ = scexao_pol.help_message()
    args = docopt(__doc__, options_first=True)
    posns = None
    if len(sys.argv) == 1:
        print(__doc__)
        return
    if args["position"] or args["status"]:
        posn = scexao_pol.get_position()
        print(posn)
    elif args["home"]:
        scexao_pol.home()
    elif args["goto"]:
        angle = float(args["<angle>"])
        scexao_pol.move_absolute(angle)
    elif args["nudge"]:
        rel_angle = float(args["<angle>"])
        scexao_pol.move_relative(rel_angle)
    elif args["stop"]:
        scexao_pol.stop()
    elif args["reset"]:
        scexao_pol.reset()
    scexao_pol.update_keys(posns)


if __name__ == "__main__":
    main()
