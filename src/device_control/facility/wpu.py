import subprocess

__all__ = ["WPU"]

class WPUDevice:

    def send_command(self, command: str):
        cmd = f"ssh wpu echo '{command}' | nc localhost 18902"
        subprocess.run(cmd.split())

    def ask_command(self, command: str):
        cmd = f"ssh wpu echo '{command}' | nc localhost 18902"
        response = subprocess.run(cmd.split(), capture_output=True)
        return response.stdout.decode()

class WPU_LP(WPUDevice):

    def get_state(self):
        pass

    def insert(self):
        self.send_command("spp move 55.2")

    def retract(self):
        self.send_command("spp move 0")



class WPU_QWP(WPUDevice):

    def get_state(self):
        pass

    def get_position(self):
        pass

    def move_absolute(self, value):
        self.send_command(f"qwp move {value}")

    def insert(self):
        self.send_command("sqw move 56")

    def retract(self):
        self.send_command("sqw move 0")



class WPU_HWP(WPUDevice):

    def get_state(self):
        pass

    def get_position(self):
        return self.ask_command(f"hwp status")


    def move_absolute(self, value):
        self.send_command(f"hwp move {value}")

    def insert(self):
        self.send_command("shw move 56")

    def retract(self):
        self.send_command("shw move 0")


class WPU:

    def __init__(self, *args, **kwargs) -> None:
        self.polarizer = WPU_LP()
        self.hwp = WPU_HWP()
        self.qwp = WPU_QWP()

    def status(self):
        f"""
        Polarizer: {self.polarizer.get_state()}
        HWP: {self.hwp.get_state()} {{ {self.hwp.get_position():.02f}° }}
        """