from dataclasses import dataclass

from .governor import Governor


@dataclass(unsafe_hash=True, kw_only=True)
class IEEEG1(Governor):
    """Governor of type IEEE G1."""

    connector_names = ["In", "Out"]

    K: float
    """Controller gain in p.u."""
    T1: float
    """Governor time constant in seconds."""
    T2: float
    """Governor deriative time constant in seconds."""
    T3: float
    """Servo time constant in seconds."""
    K1: float
    """High pressure turbine factor in p.u."""
    K2: float
    """High pressure turbine factor in p.u."""
    T5: float
    """Intermediate pressure time constant in seconds."""
    K3: float
    """Intermediate pressure turbine factor in p.u."""
    K4: float
    """Intermediate pressure turbine factor in p.u."""
    T6: float
    """Medium pressure turbine time constant in seconds."""
    K5: float
    """Medium pressure turbine factor in p.u."""
    K6: float
    """Medium pressure turbine factor in p.u."""
    T4: float
    """High pressure turbine constant in seconds."""
    T7: float
    """Low pressure turbine time constant in seconds."""
    K7: float
    """Low pressure turbine factor in p.u."""
    K8: float
    """Low pressure turbine factor in p.u."""
    Uc: float
    """Valve closing time in p.u. per second."""
    Pmin: float
    """Minimum gate limit in p.u."""
    Uo: float
    """Valve opening time in p.u. per second."""
    Pmax: float
    """Maximum gate limit in p.u."""
    db: float
    """Speed deviation deadband [p.u.]"""
    PNhp: float
    """HP Turbine Rated Power [MW]"""
    PNlp: float
    """LP Turbine Rated Power [MW]"""
