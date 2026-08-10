from dataclasses import dataclass, field
from enum import Enum

from .component import Component


class LoadType(Enum):
    """Defines the type of a load."""

    GENERAL = "General"
    LOW_VOLTAGE = "Low Voltage"


@dataclass(unsafe_hash=True, kw_only=True)
class Load(Component):
    """This class represents a load."""

    active_power: float = field(default_factory=float)
    """The active power of the load. The unit is MW."""

    reactive_power: float = field(default_factory=float)
    """The reactive power of the load. The unit is Mvar."""

    load_type: LoadType = LoadType.GENERAL
    """The load type. General load is used by default."""