from dataclasses import dataclass
from enum import Enum

from .power_system_stabilizer import PowerSystemStabilizer


class PSS1AInputSelector(Enum):
    """Enumeration for the input type selector of an IEEE PSS1A."""

    P_GEN = "P_GEN"
    """Generator electrical power [p.u.]"""
    W = "W"
    """Generator (rotor) speed [p.u.]"""
    W_DEV = "W_DEV"
    """Generator (rotor) speed deviation [p.u.]"""
    F = "F"
    """Bus frequency [p.u.]"""
    F_DEV = "F_DEV"
    """Bus frequency deviation [p.u.]"""


@dataclass(unsafe_hash=True, kw_only=True)
class IEEEPSS1A(PowerSystemStabilizer):
    """PSS of type IEEE PSS1A."""

    connector_names = ["In", "Out"]

    Vsi_in: PSS1AInputSelector
    """Input type selector."""
    Ks: float
    """PSS gain [p.u.]"""
    A1: float
    """Notch filter (2nd order block) constant [s]"""
    A2: float
    """Notch filter (2nd order block) constant [s^2]"""
    T1: float
    """Lead compensating time constant 1 [s]"""
    T2: float
    """Lag compensating time constant 1 [s]"""
    T3: float
    """Lead compensating time constant 2 [s]"""
    T4: float
    """Lag compensating time constant 2 [s]"""
    T5: float
    """Washout time constant [s]"""
    T6: float
    """Transducer time constant [s]"""
    Vst_min: float
    """Minimum PSS output [p.u.]"""
    Vst_max: float
    """Maximum PSS output [p.u.]"""
