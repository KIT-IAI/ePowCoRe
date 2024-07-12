from dataclasses import dataclass

from .exciter import Exciter


@dataclass(unsafe_hash=True, kw_only=True)
class SEXS(Exciter):
    """Exciter of the type SEXS (simplified excitation system)."""

    connector_names = ["In", "Out"]

    Ta: float
    """Filter lead time constant [s]"""
    Tb: float
    """Filter lag time constant [s]"""
    K: float
    """Controller gain [p.u.]"""
    Te: float
    """Exciter time constant [s]"""
    Emin: float
    """Exciter minimum output [p.u.]"""
    Emax: float
    """Exciter maximum output [p.u.]"""
