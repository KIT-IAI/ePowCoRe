from dataclasses import dataclass

from .component import Component


@dataclass(unsafe_hash=True, kw_only=True)
class Shunt(Component):
    """A shunt defined by conductance and susceptance."""

    p: float
    """Active power demand at 1.0 p.u. voltage in MW."""
    q: float
    """Reactive power demand at 1.0 p.u. voltage in Mvar."""
