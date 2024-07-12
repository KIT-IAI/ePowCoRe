import matlab.engine
from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.core_model import CoreModel
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.SYNC_MACHINE
BUS_TYPES = {
    LFBusType.PV: "PV",
    LFBusType.PQ: "PQ",
    LFBusType.SL: "swing",
}


def create_generator(
    eng: matlab.engine.MatlabEngine,
    generator: SynchronousMachine,
    core_model: CoreModel,
    model_name: str,
) -> SimscapeBlock:
    """Create a Simscape block for the generator."""
    block_name = f"{model_name}/{generator.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)

    graph = core_model.graph
    bus_neighbors = [n for n in graph.neighbors(generator) if isinstance(n, Bus)]
    bus = bus_neighbors[0] if len(bus_neighbors) > 0 else None
    eng.set_param(
        block_name,
        "Position",
        "[825 285 915 365]",
        "RotorType",
        "Round",
        "NominalParameters",
        f"[{generator.rated_apparent_power*1e6},{generator.rated_voltage*1e3},{core_model.base_frequency}]",
        "Reactances1",
        f"[{generator.synchronous_reactance_x:.4f},{generator.transient_reactance_x:.4f},"
        + f"{generator.subtransient_reactance_x:.4f},{generator.synchronous_reactance_q:.4f},"
        + f"{generator.transient_reactance_q:.4f},{generator.subtransient_reactance_q:.4f},"
        + f"{generator.stator_leakage_reactance:.4f}]",
        "dAxisTimeConstants",
        "Open-circuit",
        "qAxisTimeConstants",
        "Open-circuit",
        "TimeConstants8",
        "[ 8.0, 0.03, 1.0, 0.07 ]",
        "StatorResistance",
        "0.037875",
        "Mechanical",
        f"[{generator.inertia_constant:.4f} 0 2]",
        "InitialConditions",
        "[ 0  0  0  0  0  0  0  0  1 ]",
        "SetSaturation",
        "Off",
        "Pref",
        f"{generator.active_power * 1e6}",
        nargout=0,
    )

    if bus is not None:
        if bus.lf_bus_type == LFBusType.PQ:
            eng.set_param(block_name, "Qref", f"{generator.reactive_power * 1e6}", nargout=0)
        elif bus.lf_bus_type == LFBusType.PV:
            eng.set_param(
                block_name,
                "Qmin",
                f"{generator.qc1_min * 1e6}",
                "Qmax",
                f"{generator.qc1_max * 1e6}",
                nargout=0,
            )
        eng.set_param(
            block_name,
            "BusType",
            BUS_TYPES[bus.lf_bus_type],
            nargout=0,
        )
    else:
        # Set default bus type to PV
        eng.set_param(
            block_name,
            "BusType",
            "PV",
            nargout=0,
        )

    return SimscapeBlock(block_name, BLOCK_TYPE)
