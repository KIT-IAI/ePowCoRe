import matlab.engine
from epowcore.gdf.bus import Bus
from epowcore.gdf.generators.static_generator import StaticGenerator
from epowcore.gdf.core_model import CoreModel
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.STATIC_GEN


def create_static_generator(
    eng: matlab.engine.MatlabEngine,
    gen: StaticGenerator,
    core_model: CoreModel,
    model_name: str,
) -> SimscapeBlock:
    """Create a Simscape block for the static generator."""
    block_name = f"{model_name}/{gen.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)

    graph = core_model.graph
    bus_neighbors = [n for n in graph.neighbors(gen) if isinstance(n, Bus)]
    bus = bus_neighbors[0] if len(bus_neighbors) > 0 else None

    if bus is None:
        raise ValueError(f"Static generator {gen.name} has no bus.")

    eng.set_param(
        block_name,
        "Position",
        "[825 285 915 365]",
        "NominalVoltage",
        f"[{bus.nominal_voltage*1e3}, {core_model.base_frequency}]",
        "ActiveReactivePowers",
        f"[{-1*gen.active_power*1e6}, {-1*gen.reactive_power*1e6}]",
        "PositiveSequence",
        "[1 0]",
        "NpNq",
        "[1 1]",
        "TimeConstants",
        "[0 0 0 0]",
        "MinimumVoltage",
        "0.7",
        "Tfilter",
        "1e-4",
        nargout=0,
    )

    return SimscapeBlock(block_name, BLOCK_TYPE)
