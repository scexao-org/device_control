from device_control.base import ConfigurableDevice
from swmain.autoretry import autoretry


def parse_status(bytevalues):
    statbits = int(bytevalues, base=16)
    output = {
        "enabled": bool(statbits & 0b1),
        "mode": statbits & 0b10,
        "alarm": bool(statbits & 0b1000000),
        "paused": bool(statbits & 0b10000000),
    }
    if statbits & 0b10000:
        output["unit"] = "C"
    elif statbits & 0b100000:
        output["unit"] = "F"
    else:
        output["unit"] = "K"
    return output


class ThorlabsTC(ConfigurableDevice):
    def __init__(self, serial_kwargs, temp, autoenable=True, **kwargs):
        serial_kwargs = dict({"baudrate": 115200}, **serial_kwargs)
        super().__init__(serial_kwargs=serial_kwargs, **kwargs)
        self.set_target(temp)

    def send_command(self, cmd: str):
        with self.serial as serial:
            serial.write(f"{cmd}\r".encode())
            # time.sleep(0.5)
            cmd_resp = serial.read_until(b"\r")
            assert cmd_resp.strip().decode() == cmd
            serial.read_until(b"> ")

    def ask_command(self, cmd: str):
        with self.serial as serial:
            serial.write(f"{cmd}\r".encode())
            # time.sleep(0.5)
            cmd_resp = serial.read_until(b"\r")
            assert cmd_resp.strip().decode() == cmd
            resp = serial.read_until(b"\r")
            serial.read_until(b"> ")
        return resp.strip().decode()

    def get_target(self):
        result = self.ask_command("tset?")
        return float(result.split()[0])

    def set_target(self, value: float):
        self.send_command(f"tset={value:.01f}")

    def get_temp(self):
        result = self.ask_command("tact?")
        return float(result.split()[0])

    def get_aux_temp(self):
        result = self.ask_command("taux?")
        return float(result.split()[0])

    def status(self):
        with self.serial as serial:
            serial.write(b"stat?\r")
            serial.read_until(b"\r")
            result = serial.read(2)
        return parse_status(result)

    def get_id(self):
        return self.ask_command("*idn?")

    def enable(self):
        status = self.status()
        if not status["enabled"]:
            self.send_command("ens")

    def disable(self):
        status = self.status()
        if status["enabled"]:
            self.send_command("ens")

    def get_status(self):
        stat_dict = self.status()
        enabled_str = "Enabled" if stat_dict["enabled"] else "Disabled"
        flc_temp = self.get_temp()
        targ_temp = self.get_target()
        output = self.format_str.format(enabled_str, flc_temp, targ_temp)
        return flc_temp, output
