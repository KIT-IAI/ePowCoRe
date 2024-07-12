from dataclasses import dataclass

from .generator import Generator


@dataclass(unsafe_hash=True, kw_only=True)
class StaticGenerator(Generator):
    """A static generator."""

    rated_apparent_power: float
    """Rated apparent power [MVA]"""
    rated_active_power: float
    """Rated active power [MW]"""

    active_power: float
    """Active power output [MW]"""
    reactive_power: float
    """Reactive power output [Mvar]"""
    voltage_set_point: float
    """Voltage setpoint [p.u.]"""

    p_min: float
    """Minimum active power output in MW."""
    p_max: float
    """Maximum active power output in MW."""
    q_min: float
    """Minimum reactive power output in Mvar."""
    q_max: float
    """Maximum reactive power output in Mvar."""
