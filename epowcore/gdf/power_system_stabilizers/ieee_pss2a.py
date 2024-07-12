from dataclasses import dataclass
from enum import Enum

from .power_system_stabilizer import PowerSystemStabilizer


class PSS2AInputSelector(Enum):
    """Enumeration for the input type selector of an IEEE PSS2A."""

    NONE = "NONE"
    """No input"""
    W_DEV = "W_DEV"
    """Generator (rotor) speed deviation [p.u.]"""
    F_DEV = "F_DEV"
    """Bus frequency deviation [p.u.]"""
    P_GEN_EL = "P_GEN_EL"
    """Generator electrical power [p.u.]"""
    P_GEN_ACC = "P_GEN_ACC"
    """Generator accelerating power [p.u.]"""
    V_BUS = "V_BUS"
    """Bus voltage [p.u.]"""
    VD_BUS = "VD_BUS"
    """Bus voltage derivative [p.u.]"""


@dataclass(unsafe_hash=True, kw_only=True)
class IEEEPSS2A(PowerSystemStabilizer):
    """PSS of type IEEE PSS2A."""

    connector_names = ["In", "Out"]

    In1: PSS2AInputSelector
    """Input 1 type selector."""
    In2: PSS2AInputSelector
    """Input 2 type selector."""

    Tw1: float
    """First washout time constant on signal 1 [s]"""
    Tw2: float
    """Second washout time constant on signal 1 [s]"""
    Tw3: float
    """First washout time constant on signal 2 [s]"""
    Tw4: float
    """Second washout time constant on signal 2 [s]"""

    T6: float
    """Transducer time constant on signal 1 [s]"""
    T7: float
    """Transducer time constant on signal 2 [s]"""
    Ks2: float
    """Transducer gain on signal 2 [p.u.]"""
    Ks3: float
    """Washout coupling factor [p.u.]"""
    T8: float
    """Lead of ramp tracking filter [s]"""
    T9: float
    """Lag of ramp tracking filter [s]"""
    M: float
    """Ramp tracking filter M exponent"""
    N: float
    """Ramp tracking filter N exponent"""

    Ks1: float
    """PSS gain [p.u.]"""
    Ts1: float
    """1st lead time constant [s]"""
    Ts2: float
    """1st lag time constant [s]"""
    Ts3: float
    """2nd lead time constant [s]"""
    Ts4: float
    """2nd lag time constant [s]"""

    Vst_min: float
    """Minimum PSS output [p.u.]"""
    Vst_max: float
    """Maximum PSS output [p.u.]"""
