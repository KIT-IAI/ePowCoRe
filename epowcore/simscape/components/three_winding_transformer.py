import matlab.engine
from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.data_structure import DataStructure
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.THW_TRANSFORMER


def create_thw_trans(
    eng: matlab.engine.MatlabEngine,
    thw_trans: ThreeWindingTransformer,
    data_structure: DataStructure,
    model_name: str,
) -> SimscapeBlock:
    """Create a Simscape block for the three winding transformer."""
    f = data_structure.base_frequency
    block_name = f"{model_name}/{thw_trans.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)

    # TODO: Set correct parameters r1_xx, x1_xx
    eng.set_param(
        block_name,
        "Winding1Connection",
        "Yg",
        "Winding2Connection",
        "Yg",
        "Winding3Connection",
        "Yg",
        "CoreType",
        "Three single-phase transformers",
        "UNITS",
        "pu",
        "NominalPower",
        f"[ {thw_trans.rating_hv},{f}]",
        "Winding1",
        f"[ {thw_trans.voltage_hv} , {thw_trans.r1_hm} , {thw_trans.x1_hm} ]",
        "Winding2",
        f"[ {thw_trans.voltage_mv}, {thw_trans.r1_ml} , {thw_trans.x1_ml} ]",
        "Winding3",
        f"[ {thw_trans.voltage_lv} , {thw_trans.r1_lh} , {thw_trans.x1_lh} ]",
        "Rm",
        "500",
        "Lm",
        "500",
        nargout=0,
    )

    return SimscapeBlock(block_name, BLOCK_TYPE)
