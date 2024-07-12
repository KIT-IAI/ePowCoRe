import matlab.engine

from epowcore.gdf.transformers.transformer import WindingConfig
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.data_structure import DataStructure
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.TW_TRANSFORMER


def create_tw_trans(
    eng: matlab.engine.MatlabEngine,
    tw_trans: TwoWindingTransformer,
    data_structure: DataStructure,
    model_name: str,
) -> SimscapeBlock:
    """Create a Simscape block for the two winding transformer."""
    block_name = f"{model_name}/{tw_trans.name}"
    f = data_structure.base_frequency
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)
    eng.set_param(
        block_name,
        "Winding1Connection",
        _get_winding_config(tw_trans.connection_type_hv_fb),
        "Winding2Connection",
        _get_winding_config(tw_trans.connection_type_lv_fb),
        "CoreType",
        "Three single-phase transformers",
        "UNITS",
        "pu",
        "NominalPower",
        f"[{tw_trans.rating * 1e6:3g} {f}]",
        "Winding1",
        f"[{tw_trans.voltage_hv * 1e3 * tw_trans.tap_ratio_fb():3g} {tw_trans.r1pu/2:4g} {tw_trans.x1pu/2:4g}]",
        "Winding2",
        f"[{tw_trans.voltage_lv * 1e3:3g} {tw_trans.r1pu/2:4g} {tw_trans.x1pu/2:4g}]",
        "Rm",
        f"{tw_trans.rm_pu:4g}",
        "Lm",
        f"{tw_trans.xm_pu:4g}",
        "Position",
        "[700 20 770 85]",
        nargout=0,
    )
    return SimscapeBlock(block_name, BLOCK_TYPE)


def _get_winding_config(config: WindingConfig) -> str:
    if config in [WindingConfig.Y, WindingConfig.YN]:
        return "Yg"
    return "Delta (D1)"
