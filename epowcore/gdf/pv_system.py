from dataclasses import dataclass, field

from epowcore.gdf.component import Component


@dataclass(unsafe_hash=True, kw_only=True)
class PVSystem(Component):
    """A simple photovoltaic system."""

    rated_power: float = field(default_factory=float)
    """Rated power in MVA."""
    real_power_output: float = field(default_factory=float)
    """Real power output in MW."""
    reactive_power_output: float = field(default_factory=float)
    """Reactive power output in Mvar."""
    minimum_real_power_output: float = field(default_factory=float)
    """Minimum real power output in MW."""
    maximum_real_power_output: float = field(default_factory=float)
    """Maximum real power output in MW."""
    minimum_reactive_power_output: float = field(default_factory=float)
    """Minimum reactive power output in Mvar."""
    maximum_reactive_power_output: float = field(default_factory=float)
    """Maximum reactive power output in Mvar."""
