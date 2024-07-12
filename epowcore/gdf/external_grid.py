from dataclasses import dataclass
from enum import Enum

from .component import Component


class ExternalGridType(Enum):
    """Enum for the different types of power grids"""

    # PQ: P and Q must be specified
    PQ = "PQ"
    # PV: P and V must be specified
    PV = "PV"
    # SL: V must be specified
    SL = "SL"


@dataclass(unsafe_hash=True, kw_only=True)
class ExternalGrid(Component):
    """An external electrical grid, defined as a bus."""

    u_setp: float
    """Voltage setpoint [pu]."""
    p: float
    """Active power [MW]."""
    q: float
    """Reactive power [Mvar]."""
    p_min: float | None = None
    """Minimum active power [MW]."""
    p_max: float | None = None
    """Maximum active power [MW]."""
    q_min: float
    """Minimum reactive power [Mvar]."""
    q_max: float
    """Maximum reactive power [Mvar]."""
    bus_type: ExternalGridType
    """Bus type."""
