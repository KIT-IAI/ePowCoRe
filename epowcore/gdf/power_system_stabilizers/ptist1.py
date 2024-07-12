from dataclasses import dataclass

from .power_system_stabilizer import PowerSystemStabilizer


@dataclass(unsafe_hash=True, kw_only=True)
class PTIST1(PowerSystemStabilizer):
    """PSS of type PTIST1."""

    connector_names = ["In", "Out"]

    Kpss: float
    """Stabilizer gain in p.u."""
    Tw: float
    """Washout integrate time constant"""
    T1: float
    """First lead/lag deriative time constant"""
    T2: float
    """First lead/lag delay time constant"""
    T3: float
    """Second lead/lag deriative time constant"""
    T4: float
    """Second lead/lag delay time constant"""
