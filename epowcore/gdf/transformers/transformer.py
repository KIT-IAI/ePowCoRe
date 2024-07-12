from enum import Enum
from typing import NamedTuple
from epowcore.gdf.component import Component


class Transformer(Component):
    """Abstract class for Transformer elements"""


class WindingConfig(Enum):
    """Enum that defines the available winding configurations for transformers.

    - `D`: Delta (Mesh)
    - `Y`: Wye (Star)
    - `Z`: Zig-Zag (Interconnected Star)

    The `N` suffix indicates the neutral point being available for a connection.
    """

    Y = "Y"
    YN = "YN"
    Z = "Z"
    ZN = "ZN"
    D = "D"


class TapDetails(NamedTuple):
    """Detailed information about a tap changer. Does not include tap ratio."""

    tap_changer_voltage: float
    """Voltage change per tap in p.u."""
    tap_min: int
    """Tap changer for negative direction in negative values"""
    tap_max: int
    """Tap changer for positive direction in positive values"""
    tap_neutral: int
    """Number where neutral position of the tap changer is at"""
    tap_initial: int
    """Number where initial position of the tap changer is at"""


# common winding connections according to IEC 60076-1
PHASE_SHIFT_CONNECTIONS: dict[int, tuple[WindingConfig, WindingConfig]] = {
    0: (WindingConfig.YN, WindingConfig.YN),  #   Yy0
    30: (WindingConfig.YN, WindingConfig.D),  #   Yd1
    60: (WindingConfig.D, WindingConfig.D),  #    Dd2
    120: (WindingConfig.D, WindingConfig.D),  #   Dd4
    150: (WindingConfig.YN, WindingConfig.D),  #  Yd5
    180: (WindingConfig.YN, WindingConfig.YN),  # YY6
    210: (WindingConfig.YN, WindingConfig.D),  #  Yd7
    240: (WindingConfig.D, WindingConfig.D),  #   Dd8
    300: (WindingConfig.D, WindingConfig.D),  #   Dd10
    330: (WindingConfig.YN, WindingConfig.D),  #  Yd11
}


def connections_for_phase_shift(phase_shift: int) -> tuple[WindingConfig, WindingConfig]:
    """Get a common combination of winding connections for the given phase shift.

    :param phase_shift: Phase shift [deg]
    :type phase_shift: int
    :return: Configurations for primary and secondary winding
    :rtype: tuple[WindingConfig, WindingConfig]
    """
    result = PHASE_SHIFT_CONNECTIONS.get(phase_shift % 360, None)
    if result is None:
        raise ValueError(f"Unsupported phase shift: {phase_shift}. Must be a multiple of 30.")
    return result
