import subprocess
from swmain.redis import update_keys
import click

__all__ = ["WPU"]


class WPUDevice:
    def send_command(self, command: str):
        cmd = f'ssh wpu "echo {command} | nc localhost 18902"'
        response = subprocess.run([cmd], shell=True)
        response.check_returncode()

    def ask_command(self, command: str):
        cmd = f'ssh wpu "echo {command} | nc localhost 18902"'
        response = subprocess.run([cmd], shell=True, capture_output=True)
        response.check_returncode()
        return response.stdout.decode()


class WPU_SPP(WPUDevice):
    def get_status(self):
        status = self.ask_command("spp status")
        tokens = status.split()
        pos_idx = tokens.index("position") + 1
        targ_idx = tokens.index("target") + 1
        mode_idx = tokens.index("mode") + 1
        polang_idx = tokens.index("pol_angle") + 1
        status = {
            "position": float(tokens[pos_idx]),
            "target": float(tokens[targ_idx]),
            "mode": tokens[mode_idx],
            "pol_angle": float(tokens[polang_idx]),
        }
        self.update_keys(status)
        return status

    def update_keys(self, status=None):
        # TODO
        pass

    def get_position(self):
        status = self.get_status()
        return status["position"]

    def move_in(self):
        self.send_command("spp move 55.2")

    def move_out(self):
        self.send_command("spp move 0")


class WPU_SHW(WPUDevice):
    def get_status(self):
        status = self.ask_command("shw status")
        tokens = status.split()
        pos_idx = tokens.index("position") + 1
        targ_idx = tokens.index("target") + 1
        mode_idx = tokens.index("mode") + 1
        status = {
            "position": float(tokens[pos_idx]),
            "target": float(tokens[targ_idx]),
            "mode": tokens[mode_idx],
        }
        self.update_keys(status)
        return status

    def update_keys(self, status=None):
        pass
        # update_keys(**mapping)

    def get_position(self):
        status = self.get_status()
        return status["position"]

    def move_absolute(self, value):
        self.send_command(f"shw move {value}")

    def move_in(self):
        self.move_absolute(56)

    def move_out(self):
        self.move_absolute(0)


class WPU_SQW(WPUDevice):
    def get_status(self):
        status = self.ask_command("sqw status")
        tokens = status.split()
        pos_idx = tokens.index("position") + 1
        targ_idx = tokens.index("target") + 1
        mode_idx = tokens.index("mode") + 1
        status = {
            "position": float(tokens[pos_idx]),
            "target": float(tokens[targ_idx]),
            "mode": tokens[mode_idx],
        }
        self.update_keys(status)
        return status

    def update_keys(self, status=None):
        pass
        # update_keys(**mapping)

    def get_position(self):
        status = self.get_status()
        return status["position"]

    def move_absolute(self, value):
        self.send_command(f"sqw move {value}")

    def move_in(self):
        self.move_absolute(56)

    def move_out(self):
        self.move_absolute(0)


class WPU_HWP(WPUDevice):
    def get_status(self):
        status = self.ask_command("hwp status")
        tokens = status.split()
        pos_idx = tokens.index("position") + 1
        targ_idx = tokens.index("target") + 1
        mode_idx = tokens.index("mode") + 1
        polang_idx = tokens.index("pol_angle") + 1
        status = {
            "position": float(tokens[pos_idx]),
            "target": float(tokens[targ_idx]),
            "mode": tokens[mode_idx],
            "pol_angle": float(tokens[polang_idx]),
        }
        self.update_keys(status)
        return status

    def update_keys(self, status=None):
        if status is None:
            status = self.get_status()
        mapping = {
            "RET-POS1": status["position"],
            "RET-ANG1": status["pol_angle"],
            "RET-MOD1": status["mode"],
        }
        # TODO: update with redis after run
        # update_keys(**mapping)

    def get_position(self):
        status = self.get_status()
        return status["position"]

    def get_pol_angle(self):
        status = self.get_status()
        return status["pol_angle"]

    def move_absolute(self, value):
        self.send_command(f"hwp move {value}")


class WPU_QWP(WPUDevice):
    def get_status(self):
        status = self.ask_command("qwp status")
        tokens = status.split()
        pos_idx = tokens.index("position") + 1
        targ_idx = tokens.index("target") + 1
        mode_idx = tokens.index("mode") + 1
        polang_idx = tokens.index("pol_angle") + 1
        status = {
            "position": float(tokens[pos_idx]),
            "target": float(tokens[targ_idx]),
            "mode": tokens[mode_idx],
            "pol_angle": float(tokens[polang_idx]),
        }
        self.update_keys(status)
        return status

    def update_keys(self, status=None):
        if status is None:
            status = self.get_status()
        mapping = {
            "RET-POS2": status["position"],
            "RET-ANG2": status["pol_angle"],
            "RET-MOD2": status["mode"],
        }
        # TODO: update with redis after run
        # update_keys(**mapping)

    def get_position(self):
        status = self.get_status()
        return status["position"]

    def get_pol_angle(self):
        status = self.get_status()
        return status["pol_angle"]

    def move_absolute(self, value):
        self.send_command(f"qwp move {value}")


class WPU:
    def __init__(self, *args, **kwargs) -> None:
        self.spp = WPU_SPP()
        self.shw = WPU_SHW()
        self.sqw = WPU_SQW()
        self.hwp = WPU_HWP()
        self.qwp = WPU_QWP()

    def get_status(self):
        spp_status = self.spp.get_status()
        shw_status = self.shw.get_status()
        sqw_status = self.sqw.get_status()
        hwp_status = self.hwp.get_status()
        qwp_status = self.qwp.get_status()
        status = f"""{'Polarizer':9s}: {spp_status['mode']:12s} {{ {spp_status['position']:4.01f} mm }}
{'HWP stage':9s}: {shw_status['mode']:12s} {{ {shw_status['position']:4.01f} mm }}
{'QWP stage':9s}: {sqw_status['mode']:12s} {{ {sqw_status['position']:4.01f} mm }}
{'HWP':9s}: {hwp_status['mode']:12s} {{ pol={hwp_status['pol_angle']:6.02f}° wheel={hwp_status['position']:6.02f}° }}
{'QWP':9s}: {qwp_status['mode']:12s} {{ pol={qwp_status['pol_angle']:6.02f}° wheel={qwp_status['position']:6.02f}° }}"""
        return status


@click.group("wpu")
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)
    ctx.obj["wpu"] = WPU()


@main.command("status")
@click.pass_obj
def status(obj):
    print(obj["wpu"].get_status())


if __name__ == "__main__":
    main()
