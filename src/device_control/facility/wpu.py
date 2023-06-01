import socket

__all__ = ["WPU"]

class SocketDevice:

    def __init__(self, *args, **kwargs):
        self.host = "garde.sum.naoj.org"
        self.port = 18902
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def ask_command(self, command):
        raise NotImplementedError()
        with self.socket as sock:
            sock.connect((self.host, self.port))
            sock.send(command.encode())
            # return sock.r.decode()

    def send_command(self, command):
        with self.socket as sock:
            sock.connect((self.host, self.port))
            sock.send(command.encode())
    

class WPU_LP(SocketDevice):
    def get_state(self):
        pass
    def get_position(self):
        pass

    def move_absolute(self, value):
        self.send_command(f"qwp move {value}") # TODO qwp??
        
    def insert(self):
        self.send_command("spp move 55.2")

    def retract(self):
        self.send_command("spp move 0")


class WPU_HWP(SocketDevice):
    
    def get_status(self):
        pass

    def get_position(self):
        pass

    def move_absolute(self, value):
        self.send_command(f"hwp move {value}")
        
    def insert(self):
        self.send_command("shw move 56")

    def retract(self):
        self.send_command("shw move 0")


class WPU:

    def __init__(self) -> None:
        self.polarizer = WPU_LP()
        self.hwp = WPU_HWP()

