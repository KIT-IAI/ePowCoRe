from dataclasses import dataclass

from .governor import Governor


@dataclass(unsafe_hash=True, kw_only=True)
class GAST(Governor):
    """Governor of type GAST (gas turbine model with governor)."""

    connector_names = ["In", "Out"]

    R: float
    """Speed droop [p.u.]"""
    T1: float
    """Governor time constant [s]"""
    T2: float
    """Turbine power time constant [s]"""
    T3: float
    """Compressor time constant [s]"""
    AT: float
    """Ambient temperature load limit [p.u.]"""
    KT: float
    """Temperature limiter gain [p.u.]"""
    Vmin: float
    """Minimum turbine power output [p.u.]"""
    Vmax: float
    """Maximum turbine power output [p.u.]"""
    Dturb: float
    """Turbine damping factor [p.u.]"""
