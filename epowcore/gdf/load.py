from dataclasses import dataclass, field

from .component import Component


# The attributes are never changed after being insterted into a structure requiring hashes
@dataclass(unsafe_hash=True, kw_only=True)
class Load(Component):
    """This class represents an general Load. Specific kinds
    of loads are not taken into account currently."""

    active_power: float = field(default_factory=float)
    """The active power of the Load. The unit is MW."""
    reactive_power: float = field(default_factory=float)
    """The reactive Power of the Load. The unit is Mvar."""
