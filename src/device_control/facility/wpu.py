import click
from paramiko import AutoAddPolicy, SSHClient

from swmain.redis import update_keys

__all__ = ["WPU"]


class WPUDevice:
    def __init__(self, client: SSHClient = None) -> None:
        if client is None:
            self.client = SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(
                hostname="garde.sum.naoj.org",
                username="ircs",
                disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
            )
        else:
            self.client = client

        self.port = 18902

    def send_command(self, command: str):
        cmd = f"echo {command} | nc localhost {self.port}"
        stdin, stdout, stderr = self.client.exec_command(cmd)

    def ask_command(self, command: str):
        cmd = f"echo {command} | nc localhost {self.port}"
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return stdout.read().decode()


class WPU_SPP(WPUDevice):
    def get_status(self):
        status = self.ask_command("spp status")
        status_dict = {
            "position": -1,
            "target": -1,
            "mode": "UNKNOWN",
            "pol_angle": -1,
        }
        if len(status) > 0:
            tokens = status.split()
            pos_idx = tokens.index("position") + 1
            targ_idx = tokens.index("target") + 1
            mode_idx = tokens.index("mode") + 1
            polang_idx = tokens.index("pol_angle") + 1
            status_dict.update(
                {
                    "position": float(tokens[pos_idx]),
                    "target": float(tokens[targ_idx]),
                    "mode": tokens[mode_idx],
                    "pol_angle": float(tokens[polang_idx]),
                }
            )
        self.update_keys(status_dict)
        return status_dict

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
        status_dict = {
            "position": -1,
            "target": -1,
            "mode": "UNKNOWN",
        }
        if len(status) > 0:
            tokens = status.split()
            pos_idx = tokens.index("position") + 1
            targ_idx = tokens.index("target") + 1
            mode_idx = tokens.index("mode") + 1
            status_dict.update(
                {
                    "position": float(tokens[pos_idx]),
                    "target": float(tokens[targ_idx]),
                    "mode": tokens[mode_idx],
                }
            )
        self.update_keys(status_dict)
        return status_dict

    def update_keys(self, status=None):
        pass

    def get_position(self):
        status = self.get_status()
        return status["position"]

    def move_absolute(self, value):
        self.send_command(f"shw move {value:.02f}")

    def move_in(self):
        self.move_absolute(56)

    def move_out(self):
        self.move_absolute(0)


class WPU_SQW(WPUDevice):
    def get_status(self):
        status = self.ask_command("sqw status")
        status_dict = {
            "position": -1,
            "target": -1,
            "mode": "UNKNOWN",
        }
        if len(status) > 0:
            tokens = status.split()
            pos_idx = tokens.index("position") + 1
            targ_idx = tokens.index("target") + 1
            mode_idx = tokens.index("mode") + 1
            status_dict.update(
                {
                    "position": float(tokens[pos_idx]),
                    "target": float(tokens[targ_idx]),
                    "mode": tokens[mode_idx],
                }
            )
        self.update_keys(status_dict)
        return status_dict

    def update_keys(self, status=None):
        pass

    def get_position(self):
        status = self.get_status()
        return status["position"]

    def move_absolute(self, value):
        self.send_command(f"sqw move {value:.02f}")

    def move_in(self):
        self.move_absolute(56)

    def move_out(self):
        self.move_absolute(0)


class WPU_HWP(WPUDevice):
    def get_status(self):
        status = self.ask_command("hwp status")
        status_dict = {
            "position": -1,
            "target": -1,
            "mode": "UNKNOWN",
            "pol_angle": -1,
        }
        if len(status) > 0:
            tokens = status.split()
            pos_idx = tokens.index("position") + 1
            targ_idx = tokens.index("target") + 1
            mode_idx = tokens.index("mode") + 1
            polang_idx = tokens.index("pol_angle") + 1
            status_dict.update(
                {
                    "position": float(tokens[pos_idx]),
                    "target": float(tokens[targ_idx]),
                    "mode": tokens[mode_idx],
                    "pol_angle": float(tokens[polang_idx]),
                }
            )
        self.update_keys(status_dict)
        return status_dict

    def update_keys(self, status=None):
        if status is None:
            status = self.get_status()
        mapping = {
            "RET-POS1": status["position"],
            "RET-ANG1": status["pol_angle"],
            "RET-MOD1": status["mode"],
        }
        update_keys(**mapping)

    def get_position(self):
        status = self.get_status()
        return status["position"]

    def get_pol_angle(self):
        status = self.get_status()
        return status["pol_angle"]

    def move_absolute(self, value):
        self.send_command(f"hwp move {value:.02f}")


class WPU_QWP(WPUDevice):
    def get_status(self):
        status = self.ask_command("qwp status")
        status_dict = {
            "position": -1,
            "target": -1,
            "mode": "UNKNOWN",
            "pol_angle": -1,
        }
        if len(status) > 0:
            tokens = status.split()
            pos_idx = tokens.index("position") + 1
            targ_idx = tokens.index("target") + 1
            mode_idx = tokens.index("mode") + 1
            polang_idx = tokens.index("pol_angle") + 1
            status_dict.update(
                {
                    "position": float(tokens[pos_idx]),
                    "target": float(tokens[targ_idx]),
                    "mode": tokens[mode_idx],
                    "pol_angle": float(tokens[polang_idx]),
                }
            )
        self.update_keys(status_dict)
        return status_dict

    def update_keys(self, status=None):
        if status is None:
            status = self.get_status()
        mapping = {
            "RET-POS2": status["position"],
            "RET-ANG2": status["pol_angle"],
            "RET-MOD2": status["mode"],
        }
        update_keys(**mapping)

    def get_position(self):
        status = self.get_status()
        return status["position"]

    def get_pol_angle(self):
        status = self.get_status()
        return status["pol_angle"]

    def move_absolute(self, value):
        self.send_command(f"qwp move {value:.02f}")


class WPU:
    def __init__(self, *args, **kwargs) -> None:
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.load_system_host_keys()
        self.client.connect(
            hostname="garde.sum.naoj.org",
            username="ircs",
            disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
        )
        self.spp = WPU_SPP(client=self.client)
        self.shw = WPU_SHW(client=self.client)
        self.sqw = WPU_SQW(client=self.client)
        self.hwp = WPU_HWP(client=self.client)
        self.qwp = WPU_QWP(client=self.client)

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
    click.echo(obj["wpu"].get_status())


if __name__ == "__main__":
    main()
