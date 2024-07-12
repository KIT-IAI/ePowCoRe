import matlab.engine
from epowcore.gdf.governors.gast import GAST
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.GAST


def create_gast(
    eng: matlab.engine.MatlabEngine, gov: GAST, model_name: str
) -> SimscapeBlock:
    """Create a Simscape block for the GAST governor."""

    block_name = f"{model_name}/{gov.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)
    set_parameters_gast(eng, gov, block_name)

    return SimscapeBlock(block_name, BLOCK_TYPE)


def set_parameters_gast(eng: matlab.engine.MatlabEngine, gov: GAST, block_name: str) -> None:
    """Set the parameter values of an existing Simscape block."""

    eng.set_param(
        block_name,
        "R",
        f"{gov.R}",
        "T_1",
        f"{gov.T1}",
        "T_2",
        f"{gov.T2}",
        "T_3",
        f"{gov.T3}",
        "A_T",
        f"{gov.AT}",
        "K_T",
        f"{gov.KT}",
        "Vmin",
        f"{gov.Vmin}",
        "Vmax",
        f"{gov.Vmax}",
        "DTurb",
        f"{gov.Dturb}",
        nargout=0,
    )
