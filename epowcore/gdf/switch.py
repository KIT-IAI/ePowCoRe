from dataclasses import dataclass, field

from .component import Component


@dataclass(unsafe_hash=True, kw_only=True)
class Switch(Component):
    """A switch."""

    closed: bool = field()
    """If set to true, the switch connects."""
    in_service: bool | None = None
    """If set to true, switch has no failure."""
    rate_a: float | None = None
    """Long term rating [MVA]."""
    rate_b: float | None = None
    """Short term rating [MVA]."""
    rate_c: float | None = None
    """Emergency rating [MVA]."""
