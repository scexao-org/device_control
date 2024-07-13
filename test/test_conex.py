from device_control.interfaces import MotionDriver, SerialDriver
from loguru import logger

__all__ = "CONEXDriver"

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
    "": None,
}


class CONEXDriver(MotionDriver, SerialDriver):
    def __init__(self, device_address=1, **kwargs):
        super().__init__(**kwargs)
        if device_address < 1 or device_address > 31:
            msg = f"controller address must be between 1 and 31, got {device_address}"
            raise ValueError(msg)
        self.device_address = device_address

    def send(self, command: str):
        # pad command with CRLF ending
        cmd = f"{self.device_address}{command}\r\n"
        logger.debug(f"sending command: {cmd[:-2]}")
        with self.serial as serial:
            serial.write(cmd.encode())
            serial.read_until(b"\r\n")

    def ask(self, command: str):
        # pad command with CRLF ending
        cmd = f"{self.device_address}{command}\r\n"
        logger.debug(f"sending command: {cmd[:-2]}")
        with self.serial as serial:
            serial.write(cmd.encode())
            resp = serial.read_until(b"\r\n")
        retval = resp.strip().decode()
        logger.debug(f"received: {retval[:-2]}")
        # strip command and \r\n from string
        value = retval.split(command.replace("?", ""))[-1]
        return value

    def get_stage_identifier(self) -> str:
        return self.ask("ID?")

    def set_stage_identifier(self, value: str):
        self.send(f"ID{value}")

    def get_rs485_address(self) -> int:
        return int(self.ask("SA?"))

    def set_rs485_address(self, value: int):
        self.send(f"SA{value}")

    def get_lower_limit(self) -> float:
        return float(self.ask("SA?"))

    def lower_limit(self, value: float):
        self.send(f"SA{value}")

    def get_upper_limit(self) -> float:
        return float(self.ask("SR?"))

    def set_upper_limit(self, value: float):
        self.send(f"SR{value}")

    def get_encoder_increment(self) -> float:
        return float(self.ask("SU?"))

    def set_encoder_increment(self, value: float):
        self.send(f"SU{value}")

    def get_error_string(self, code: str):
        return self.ask(f"TB{code}")

    def get_last_command_error(self) -> str:
        err = self.ask("TE")
        return self.error_string(err)

    def get_state(self) -> CONEXState:
        return CONEX_STATES[self.ask("MM?")]

    def is_enabled(self) -> bool:
        return not isinstance(self.get_state(), Disable)

    def is_moving(self) -> bool:
        return isinstance(self.get_state(), Moving)

    def is_homing(self) -> bool:
        return isinstance(self.get_state(), Homing)

    def is_ready(self) -> bool:
        return isinstance(self.get_state(), Ready)

    def needs_homing(self) -> bool:
        return isinstance(self.get_state(), NotReferenced)

    def disable(self):
        self.send("MM0")

    def enable(self):
        self.send("MM1")

    def reset(self):
        self.send("RS")

    def reset_address(self, value: int):
        self.send(f"RS{value}")

    def _home(self):
        self.send("OR")
        while self.is_homing():
            self.update_keys()

    def _move_absolute(self, value: float):
        # check if we're not referenced
        if self.needs_homing():
            logger.warn("CONEX device needs to be homed.")
            return
        # wait until we're ready to move
        while not self.is_ready():
            pass
        # send move command
        self.send(f"PA{value}")
        # if blocking, loop while moving
        while self.is_moving():
            self.update_keys()

    def _move_relative(self, value: float):
        # check if we're not referenced
        if self.needs_homing():
            logger.warn("CONEX device needs to be homed.")
            return
            # wait until we're ready to move
        while not self.is_ready():
            continue
        # send move command
        self.send(f"PR{value}")
        # if blocking, loop while moving
        while self.is_moving():
            self.update_keys()

    def _get_target_position(self) -> float:
        return float(self.ask("TH?"))

    def _get_position(self) -> float:
        return float(self.ask("TP"))

    def _stop(self):
        self.send("ST")
