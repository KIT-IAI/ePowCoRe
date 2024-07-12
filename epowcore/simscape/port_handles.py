from typing import NamedTuple

from epowcore.simscape.shared import SimscapeBlockType


class PortHandles(NamedTuple):
    """This class helps to find the PortHandles of Simscape blocks."""

    name: str
    """The name of the PortHandles, usually LConn or RConn"""
    start: int
    """The start index of the PortHandles"""
    length: int
    """The number of PortHandles, usually 1 or 3 (depending on the number of phases)"""
    key: str
    """The key that is used to map the edge data to the PortHandles."""


PORT_HANDLES: dict[SimscapeBlockType, dict[str, PortHandles]] = {
    SimscapeBlockType.BUS: {
        "": PortHandles(
            name="LConn",
            start=0,
            length=1,
            key="",
        ),
    },
    SimscapeBlockType.VI_MEASUREMENT: {
        "LConn": PortHandles(
            name="LConn",
            start=0,
            length=3,
            key="LConn",
        ),
        "RConn": PortHandles(
            name="RConn",
            start=0,
            length=3,
            key="RConn",
        ),
    },
    SimscapeBlockType.LOAD: {
        "": PortHandles(
            name="LConn",
            start=0,
            length=3,
            key="",
        ),
    },
    SimscapeBlockType.STATIC_GEN: {
        "": PortHandles(
            name="LConn",
            start=0,
            length=3,
            key="",
        ),
    },
    SimscapeBlockType.PI_SECTION: {
        "A": PortHandles(
            name="LConn",
            start=0,
            length=3,
            key="A",
        ),
        "B": PortHandles(
            name="RConn",
            start=0,
            length=3,
            key="B",
        ),
    },
    SimscapeBlockType.SYNC_MACHINE: {
        "ABC": PortHandles(
            name="RConn",
            start=0,
            length=3,
            key="ABC",
        ),
        "m": PortHandles(
            name="Outport",
            start=0,
            length=1,
            key="m",
        ),
        "Pm": PortHandles(
            name="Inport",
            start=0,
            length=1,
            key="Pm",
        ),
        "Vf": PortHandles(
            name="Inport",
            start=1,
            length=1,
            key="Vf",
        ),
    },
    SimscapeBlockType.TW_TRANSFORMER: {
        "HV": PortHandles(
            name="LConn",
            start=0,
            length=3,
            key="HV",
        ),
        "LV": PortHandles(
            name="RConn",
            start=0,
            length=3,
            key="LV",
        ),
    },
    SimscapeBlockType.THW_TRANSFORMER: {
        "HV": PortHandles(
            name="LConn",
            start=0,
            length=3,
            key="MV",
        ),
        "MV": PortHandles(
            name="RConn",
            start=0,
            length=3,
            key="HV",
        ),
        "LV": PortHandles(
            name="RConn",
            start=3,
            length=3,
            key="LV",
        ),
    },
    SimscapeBlockType.IEEEPSS1A: {
        "In": PortHandles(
            name="Inport",
            start=0,
            length=1,
            key="In",
        ),
        "Out": PortHandles(
            name="Outport",
            start=0,
            length=1,
            key="Out",
        ),
    },
    SimscapeBlockType.IEEEPSS2A: {
        "In": PortHandles(
            name="Inport",
            start=0,
            length=2,
            key="In",
        ),
        "Out": PortHandles(
            name="Outport",
            start=0,
            length=1,
            key="Out",
        ),
    },
    SimscapeBlockType.IEEEST1A: {
        "In": PortHandles(
            name="Inport",
            start=0,
            length=4,
            key="In",
        ),
        "Out": PortHandles(
            name="Outport",
            start=0,
            length=1,
            key="Out",
        ),
    },
    SimscapeBlockType.SEXS: {
        "In": PortHandles(
            name="Inport",
            start=0,
            length=3,
            key="In",
        ),
        "Out": PortHandles(
            name="Outport",
            start=0,
            length=1,
            key="Out",
        ),
    },
    SimscapeBlockType.IEEEG1: {
        "In": PortHandles(
            name="Inport",
            start=0,
            length=2,
            key="In",
        ),
        "Out": PortHandles(
            name="Outport",
            start=0,
            length=1,
            key="Out",
        ),
    },
    SimscapeBlockType.GAST: {
        "In": PortHandles(
            name="Inport",
            start=0,
            length=2,
            key="In",
        ),
        "Out": PortHandles(
            name="Outport",
            start=0,
            length=1,
            key="Out",
        ),
    },
    SimscapeBlockType.HYGOV: {
        "In": PortHandles(
            name="Inport",
            start=0,
            length=2,
            key="In",
        ),
        "Out": PortHandles(
            name="Outport",
            start=0,
            length=1,
            key="Out",
        ),
    },
    SimscapeBlockType.IMPEDANCE: {
        "A": PortHandles(
            name="LConn",
            start=0,
            length=3,
            key="A",
        ),
        "B": PortHandles(
            name="RConn",
            start=0,
            length=3,
            key="B",
        ),
    },
    SimscapeBlockType.COMMON_IMPEDANCE: {
        "A": PortHandles(
            name="LConn",
            start=0,
            length=3,
            key="A",
        ),
        "B": PortHandles(
            name="RConn",
            start=0,
            length=3,
            key="B",
        ),
    },
    SimscapeBlockType.SUBSYSTEM: {},
}
