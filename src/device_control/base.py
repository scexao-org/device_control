import toml
from typing import Union

__all__ = ["MotionDevice"]

# Interface for hardware devices- all subclasses must
# implement this!
class MotionDevice:

    def __init__(self, address, name="", unit=None, configurations=None, config_file=None, offset=0, **kwargs):
        self.address = address
        self.name = name
        self.unit = unit
        self.configurations = configurations
        self.config_file = config_file
        self.offset = offset

    @classmethod
    def from_config(__cls__, filename):
        with open(filename, "r") as fh:
            parameters = toml.load(fh)
        address = parameters["address"]
        name = parameters["name"]
        unit = parameters.get("unit", None)
        configurations = parameters.get("configurations", None)
        return __cls__(address=address, name=name, unit=unit, configurations=configurations, config_file=filename)

    def load_config(self, filename):
        if filename is None:
            filename = self.config_file
        with open(filename, "r") as fh:
            parameters = toml.load(fh)
        self.address = parameters["address"]
        self.name = parameters["name"]
        self.unit = parameters.get("unit", None)
        self.configurations = parameters.get("configurations", None)
        self.config_file = filename

    @property
    def position(self):
        pos = self._position + self.offset
        # replace with status update
        print(f"status of {self.name}: {pos} [{self.unit}]")
        return pos

    @property
    def _position(self):
        raise NotImplementedError()

    @property
    def target_position(self):
        pos = self._target_position + self.offset
        return pos

    @property
    def _target_position(self):
        raise NotImplementedError()

    def home(self, wait=False):
        raise NotImplementedError()

    def move_absolute(self, value, wait=False):
        raise NotImplementedError()

    def move_relative(self, value, wait=False):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def move_configuration(self, index: Union[int, str], wait=False):
        if self.configurations is None:
            raise ValueError("No configurations saved")
        if isinstance(index, int):
            return self.move_configuration_idx(index, wait=wait)
        elif isinstance(index, str):
            return self.move_configuration_name(index, wait=wait)

    def move_configuration_idx(self, idx: int, wait=False):
        for row in self.configurations:
            if row["idx"] == idx:
                return self.move_absolute(row["value"], wait=wait)
        raise ValueError(f"No configuration saved at index {idx}")


    def move_configuration_name(self, name: str, wait=False):
        for row in self.configurations:
            if row["name"] == name:
                return self.move_absolute(row["value"], wait=wait)
        raise ValueError(f"No configuration saved with name '{name}'")
