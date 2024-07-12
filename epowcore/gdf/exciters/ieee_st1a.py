from dataclasses import dataclass

from .exciter import Exciter


@dataclass(unsafe_hash=True, kw_only=True)
class IEEEST1A(Exciter):
    """Exciter of type IEEE ST1A."""

    connector_names = ["In", "Out"]

    Tr: float | None = None
    """Measurement delay [s]"""
    Ka: float
    """Voltage regulator gain [p.u.]"""
    Ta: float
    """Voltage regulator time constant [s]"""
    Tb: float
    """Regulator lag time constant [s]"""
    Tc: float
    """Regulator lead time constant [s]"""
    Tb1: float
    """Regulator lag time constant [s]"""
    Tc1: float
    """Regulator lead time constant [s]"""
    Kf: float
    """Rate feedback gain [p.u.]"""
    Tf: float
    """Rate feedback time constant [s]"""
    Kc: float
    """Rectifier loading factor [p.u.]"""
    Klr: float
    """Exciter output current limiter gain [p.u.]"""
    Ilr: float
    """Exciter output current limiter reference [p.u.]"""

    # TODO: next two params need to be Enums, because they are selectors with different meanings for different implementations of the exciter type
    Vs: float
    """PSS input selector"""
    Vuel: float
    """UEL type/position selector (0:sum, 1/2: Takeover)"""

    Vi_min: float
    """Minimum voltage error [p.u.]"""
    Va_min: float
    """Minimum regulator output [p.u.]"""
    Vr_min: float
    """Minimum exciter output [p.u.]"""
    Vi_max: float
    """Maximum voltage error [p.u.]"""
    Va_max: float
    """Maximum regulator output [p.u.]"""
    Vr_max: float
    """Maximum exciter output [p.u.]"""
