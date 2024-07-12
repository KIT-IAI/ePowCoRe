import matlab.engine
from enum import Enum
from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.BUS


class Phases(Enum):
    SINGLE = "single"
    ABC = "ABC"
    AB = "AB"
    AC = "AC"
    BC = "BC"
    A = "A"
    B = "B"
    C = "C"


def create_bus(
    eng: matlab.engine.MatlabEngine,
    bus: Bus,
    data_structure: DataStructure,
    model_name: str,
    phases: Phases = Phases.SINGLE,
) -> SimscapeBlock:
    """This method takes a generic bus model and adds an equivalent Simscape block to the model."""
    block_name = f"{model_name}/{bus.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)

    vref = 1.0
    vangle = 0.0
    if bus.lf_bus_type in [LFBusType.SL, LFBusType.PV]:
        # get the voltage setpoint from a connected generator as reference
        for n in data_structure.graph.neighbors(bus):
            if isinstance(n, SynchronousMachine):
                vset = n.voltage_set_point
                if vset is not None and vset != 1.0:
                    vref = vset
                    break

    if phases in [Phases.AB, Phases.AC, Phases.BC]:
        vref_str = f"[{vref} {vref}]"
        vangle_str = "[0 0]"
    elif phases == Phases.ABC:
        vref_str = f"[{vref} {vref} {vref}]"
        vangle_str = "[0 0 0]"
    else:
        vref_str = str(vref)
        vangle_str = str(vangle)

    eng.set_param(
        block_name,
        "Position",
        "[200 20 215 45]",
        "Phases",
        phases.value,
        "ID",
        f"{bus.uid}",
        "Vbase",
        f"{bus.nominal_voltage * 1000:.4g}",
        "Vref",
        vref_str,
        "Vangle",
        vangle_str,
        nargout=0,
    )

    return SimscapeBlock(block_name, BLOCK_TYPE)
