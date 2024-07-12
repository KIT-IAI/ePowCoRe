from dataclasses import dataclass, field

from .component import Component


@dataclass(unsafe_hash=True)
class VoltageSource(Component):
    """A voltage source."""

    u_setp: float = field(default_factory=float)
    """The voltage magnitude setpoint in pu."""
    phi_setp: float = field(default_factory=float)
    """The voltage angle setpoint in pu."""
    r_pu: float = field(default_factory=float)
    """The internal resistance in pu."""
    x_pu: float = field(default_factory=float)
    """The internal reactance in pu."""
