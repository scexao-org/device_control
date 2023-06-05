from device_control.base import SSHDevice
import re
import click


class ImageRotator(SSHDevice):
    CONF = "facility/conf_image_rotator.toml"

    def get_status(self):
        status = self.ask_command("imr st")
        lines = status.splitlines()
        status_dict = {}
        for line in lines:
            key, value = re.split(":\s+", line)
            try:
                val = float(value)
            except ValueError:
                val = value
            status_dict[key] = val
        return status_dict

    def get_position(self):
        state = self.get_status()
        return state["stage angle"]

    def move_absolute(self, value):
        self.send_command(f"imr ma {value}")

    def move_relative(self, value: float):
        self.send_command(f"imr mr {value}")


@click.group("imr", help="Simple interface for interacting with the image rotator.")
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)
    ctx.obj["imr"] = ImageRotator.connect()


@main.command("status")
@click.pass_obj
def status(obj):
    print(obj["imr"].get_position())


if __name__ == "__main__":
    main()
