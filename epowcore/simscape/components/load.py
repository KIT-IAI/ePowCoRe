import matlab.engine

from epowcore.gdf.bus import Bus
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.load import Load
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.LOAD


def create_load(
    eng: matlab.engine.MatlabEngine,
    load: Load,
    core_model: CoreModel,
    model_name: str,
) -> SimscapeBlock:
    """Create a Simscape block for the load."""
    block_name = f"{model_name}/{load.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)
    f = core_model.base_frequency
    # get connected bus for nominal voltage
    # might break, but loads should only be connected to buses
    bus = next(core_model.graph.neighbors(load), None)

    nominal_voltage = 0.0
    if isinstance(bus, Bus):
        nominal_voltage = bus.nominal_voltage * 1000

    eng.set_param(
        block_name,
        "Configuration",
        "Y (grounded)",
        "Measurements",
        "None",
        "LoadType",
        "constant PQ",
        "NominalVoltage",
        f"{nominal_voltage * 1000:.4g}",
        "NominalFrequency",
        f"{f}",
        "UnBalancedPower",
        "off",
        "ActivePower",
        f"{load.active_power*1e6}",
        "Position",
        "[ 600 20 665 85]",
        nargout=0,
    )

    if load.reactive_power > 0:
        eng.set_param(
            block_name,
            "InductivePower",
            f"{load.reactive_power*1e6}",
            "CapacitivePower",
            "0",
            nargout=0,
        )
    else:
        eng.set_param(
            block_name,
            "CapacitivePower",
            f"{abs(load.reactive_power*1e6)}",
            "InductivePower",
            "0",
            nargout=0,
        )

    return SimscapeBlock(block_name, BLOCK_TYPE)
