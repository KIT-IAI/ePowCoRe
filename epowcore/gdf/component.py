from dataclasses import dataclass, asdict, field, fields
from enum import Enum, EnumMeta
from types import UnionType
from typing import Any, ClassVar, get_args

from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import Platform
from epowcore.generic.logger import Logger


@dataclass(unsafe_hash=True)
class Component:
    """Abstract class for model components."""

    uid: int
    """ID of the element, used for the graph in the DataStructure"""
    name: str = field(hash=False)
    """Name of the component."""

    coords: tuple[float, float] | list[tuple[float, float]] | None = field(hash=False, default=None)
    """Coordinates of the component in the model."""
    connector_names: ClassVar[list[str]] = []
    """List of connectors of the component."""

    @classmethod
    def from_primitive_dict(cls, data: dict) -> "Component":
        """Create a Component from a dictionary containing primitive data types.

        :param data: The dictionary containing the Component data as primitive values.
        :type data: dict
        :return: The created Component containing the data.
        :rtype: Component
        """
        non_primitive_data = dict(data)
        if "connector_names" in non_primitive_data.keys():
            del non_primitive_data["connector_names"]

        # convert strings to enums where applicable
        for f in fields(cls):
            if f.name not in data:
                continue
            if isinstance(f.type, EnumMeta):
                non_primitive_data[f.name] = f.type[data[f.name]]
            elif isinstance(f.type, UnionType):
                for utype in get_args(f.type):
                    if isinstance(utype, EnumMeta):
                        non_primitive_data[f.name] = utype[data[f.name]]
                        break

        if "coords" not in non_primitive_data:
            non_primitive_data["coords"] = None
        elif non_primitive_data["coords"] is not None:
            if all(isinstance(i, list) for i in non_primitive_data["coords"]):
                # list of coordinates
                non_primitive_data["coords"] = [tuple(i) for i in non_primitive_data["coords"]]
            else:
                # only one pair of coordinates
                non_primitive_data["coords"] = tuple(non_primitive_data["coords"])

        return cls(**non_primitive_data)

    def get_fb(self, attr: str, platform: Platform | None = None, log: bool = True) -> Any:
        """Get the value of the attribute with fallback.
        If it is None, try getting the default value from the configuration files.
        Log usages of default variables by default.

        :param attr: The name of the requested attribute.
        :type attr: str
        :param platform: The platform to get the default value for, e.g. JMDL; defaults to None
        :type platform: Platform | None, optional
        :param log: Enable/disable logging; defaults to True
        :type log: bool, optional
        :return: The instance value or default value of [attr].
        :rtype: Any | None
        """
        val = self.__dict__[attr]
        if val is None:
            val = self.get_default(attr, platform, log)
        if val is None:
            raise ValueError(f"No default value found for: {self.__class__.__name__}.{attr}")
        return val

    def get_default(
        self, attr: str, platform: Platform | None = None, log: bool = True
    ) -> Any | None:
        """Get the default value of the requested attribute.

        Allows getting defaults for different platforms.
        Creates a log entry for getting the default value by default.

        :param attr: The name of the requested attribute.
        :type attr: str
        :param platform: The platform to get the default value for, e.g. JMDL; defaults to None
        :type platform: Platform | None, optional
        :param log: Enable/disable logging; defaults to True
        :type log: bool, optional
        :return: The default value for the attribute.
        :rtype: Any | None
        """
        result = Configuration().get_default(
            component=type(self).__name__, attr=attr, platform=platform
        )
        if log:
            Logger.log_to_selected(
                f"Using default for {type(self).__name__} '{self.name}': {attr} = {result}"
            )
        return result

    def to_export_str(self) -> str:
        """Return a simple string representation,
        containing only the class, uid and name of the Component.

        :return: A simple string representation. Can be parsed as a tuple.
        :rtype: str
        """
        return f"('{type(self).__module__}.{type(self).__name__}', {self.uid}, '{self.name}')"

    def to_primitive_dict(self) -> dict:
        """Return the dataclass as a dict containing only primitive data types.

        :return: A dictionary describing the instance with primitive data types only.
        :rtype: dict
        """
        normal_dict = asdict(self)
        primitive_dict = {}
        for k, v in normal_dict.items():
            if isinstance(v, Enum):
                primitive_dict[k] = v.name
            else:
                primitive_dict[k] = v
        return primitive_dict

    def __str__(self) -> str:
        return f"('{type(self).__name__}', {self.uid}, '{self.name}')"
