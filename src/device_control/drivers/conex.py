import logging
import time


from ..base import MotionDevice
from swmain.autoretry import autoretry

__all__ = ["CONEXDevice"]

# CONEX programmer manual
# https://www.newport.com/mam/celum/celum_assets/resources/CONEX-AGP_-_Controller_Documentation.pdf


class CONEXState:
    def __init__(self, previous=None):
        self.previous = previous

    def __repr__(self):
        output = f"{self.__class__.__name__}"
        if self.previous is not None:
            output += f" from {self.previous}"
        return output


class NotReferenced(CONEXState):
    pass


class Configuration(CONEXState):
    pass


class Homing(CONEXState):
    pass


class Moving(CONEXState):
    pass


class Ready(CONEXState):
    pass


class Disable(CONEXState):
    pass


class Reset(CONEXState):
    pass


CONEX_STATES = {
    " a": NotReferenced(Reset()),
    " b": NotReferenced(Homing()),
    " c": NotReferenced(Configuration()),
    " d": NotReferenced(Disable()),
    " e": NotReferenced(Ready()),
    " f": NotReferenced(Moving()),
    "1 ": NotReferenced("no parameters"),
    "14": Configuration(),
    "1e": Homing(),
    "28": Moving(),
    "32": Ready(Homing()),
    "33": Ready(Moving()),
    "34": Ready(Disable()),
    "3c": Disable(Ready()),
    "3d": Disable(Moving()),
}


class CONEXDevice(MotionDevice):
    def __init__(
        self,
        device_address=1,
        delay=0.1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if device_address < 1 or device_address > 31:
            raise ValueError(f"controller address must be between 1 and 31, got {device_address}")
        self.device_address = device_address
        self.delay = delay
        self.logger = logging.getLogger(self.__class__.__name__)

    @autoretry(max_retries=10)
    def send_command(self, command: str):
        # pad command with CRLF ending
        cmd = f"{self.device_address}{command}\r\n"
        self.logger.debug(f"sending command: {cmd[:-2]}")
        with self.serial as serial:
            serial.reset_input_buffer()
            serial.write(cmd.encode())

    @autoretry(max_retries=10)
    def ask_command(self, command: str):
        # pad command with CRLF ending
        cmd = f"{self.device_address}{command}\r\n"
        self.logger.debug(f"sending command: {cmd[:-2]}")
        with self.serial as serial:
            serial.reset_input_buffer()
            serial.write(cmd.encode())
            retval = serial.read_until(b"\r\n").decode()
            self.logger.debug(f"received: {retval[:-2]}")
            # strip command and \r\n from string
            return retval[3:-2]

    def get_stage_identifier(self) -> str:
        return self.ask_command("ID?")

    def set_stage_identifier(self, value: str):
        self.send_command(f"ID{value}")

    def get_rs485_address(self) -> int:
        return int(self.ask_command("SA?"))

    def set_rs485_address(self, value: int):
        self.send_command(f"SA{value}")

    def get_lower_limit(self) -> float:
        return float(self.ask_command("SA?"))

    def lower_limit(self, value: float):
        self.send_command(f"SA{value}")

    def get_upper_limit(self) -> float:
        return float(self.ask_command("SR?"))

    def set_upper_limit(self, value: float):
        self.send_command(f"SR{value}")

    def get_encoder_increment(self) -> float:
        return float(self.ask_command("SU?"))

    def set_encoder_increment(self, value: float):
        self.send_command(f"SU{value}")

    def get_error_string(self, code: str):
        return self.ask_command(f"TB{code}")

    def get_last_command_error(self) -> str:
        err = self.ask_command("TE")
        return self.error_string(err)

    def get_state(self) -> CONEXState:
        return CONEX_STATES[self.ask_command("MM?")]

    def is_enabled(self) -> bool:
        return not isinstance(self.get_state(), Disable)

    def is_moving(self) -> bool:
        return isinstance(self.get_state(), Moving)

    def is_homing(self) -> bool:
        return isinstance(self.get_state(), Homing)

    def disable(self):
        self.send_command("MM0")

    def enable(self):
        self.send_command("MM1")

    def _home(self, wait=True):
        self.send_command("OR")
        if wait:
            while self.is_homing():
                self.update_keys()
                time.sleep(self.delay)

    def _move_absolute(self, value: float, wait=True):
        self.send_command(f"PA{value}")
        if wait:
            while self.is_moving():
                self.update_keys()
                time.sleep(self.delay)

    def _move_relative(self, value: float, wait=True):
        self.send_command(f"PR{value}")
        if wait:
            while self.is_moving():
                self.update_keys()
                time.sleep(self.delay)

    def reset(self):
        self.send_command("RS")

    def reset_address(self, value: int):
        self.send_command(f"RS{value}")

    def _get_target_position(self) -> float:
        return float(self.ask_command("TH?"))

    def _get_position(self) -> float:
        return float(self.ask_command("TP"))

    def stop(self):
        self.send_command("ST")
        self.update_keys()
