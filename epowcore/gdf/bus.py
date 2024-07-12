from dataclasses import dataclass, field
from enum import Enum

from .component import Component


class LFBusType(Enum):
    """Defines the type of a bus for load flow calculations."""

    PQ = "PQ"
    PV = "PV"
    SL = "SLACK"
    ISO = "ISOLATED"


class BusType(Enum):
    """Defines the functional type of the bus."""

    BUSBAR = "Busbar"
    JUNCTION = "Junction Node"
    INTERNAL = "Internal Node"


@dataclass(unsafe_hash=True, kw_only=True)
class Bus(Component):
    """This class represents a Bus element."""

    lf_bus_type: LFBusType
    """This represents the bus type for load flow calculations."""
    nominal_voltage: float = field(default_factory=float)
    """This is the nominal voltage of the bus in kV."""
    bus_type: BusType = BusType.BUSBAR
    """This defines the functional type of the bus. Default is Busbar."""
