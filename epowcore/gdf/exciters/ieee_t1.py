from dataclasses import dataclass

from .exciter import Exciter


@dataclass(unsafe_hash=True, kw_only=True)
class IEEET1(Exciter):
    """Exciter of type IEEE T1."""

    connector_names = ["In", "Out"]

    Tr: float
    """Measurement delay in seconds."""
    Ka: float
    """Controller gain in p.u."""
    Ta: float
    """Controller time constants in seconds."""
    Ke: float
    """Exciter constant in p.u."""
    Te: float
    """Exciter time constant in seconds."""
    Kf: float
    """Stabilization path gain in p.u."""
    Tf: float
    """Stabilization path time constant in seconds."""
    E1: float
    """Saturation factor 1 in p.u."""
    Se1: float
    """Saturation factor 2 in p.u."""
    E2: float
    """Saturation factor 3 in p.u."""
    Se2: float
    """Saturation factor 4 in p.u."""
    Vrmin: float
    """Controller output minimum in p.u."""
    Vrmax: float
    """Controller output maximum in p.u."""
