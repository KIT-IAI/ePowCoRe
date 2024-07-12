from dataclasses import dataclass

from .governor import Governor


@dataclass(unsafe_hash=True, kw_only=True)
class HYGOV(Governor):
    """Governor of type HYGOV (hydro governor)."""

    connector_names = ["In", "Out"]

    R_temp: float
    """Temporary droop [p.u.]"""
    R_perm: float
    """Permanent droop [p.u.]"""
    Tr: float
    """Governor time constant [s]"""
    Tf: float
    """Filter time constant [s]"""
    Tg: float
    """Gate servo time constant [s]"""
    Tw: float
    """Water starting time constant [s]"""
    At: float
    """Turbine gain [p.u.]"""
    Dturb: float
    """Turbine damping factor [p.u.]"""
    qnl: float
    """No load flow [p.u.]"""
    Gmin: float
    """Minimum gate opening [p.u.]"""
    Gmax: float
    """Maximum gate opening [p.u.]"""
    Velm: float
    """Gate velocity limit [p.u.]"""
