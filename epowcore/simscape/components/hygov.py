import matlab.engine
from epowcore.gdf.governors.hygov import HYGOV
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.HYGOV


def create_hygov(
    eng: matlab.engine.MatlabEngine, gov: HYGOV, model_name: str
) -> SimscapeBlock:
    """Create a Simscape block for the HYGOV governor."""

    block_name = f"{model_name}/{gov.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)
    set_parameters_hygov(eng, gov, block_name)

    return SimscapeBlock(block_name, BLOCK_TYPE)


def set_parameters_hygov(eng: matlab.engine.MatlabEngine, gov: HYGOV, block_name: str) -> None:
    """Set the parameter values of an existing Simscape block."""

    eng.set_param(
        block_name,
        "Rt",
        f"{gov.R_temp}",
        "Rp",
        f"{gov.R_perm}",
        "TR",
        f"{gov.Tr}",
        "TF",
        f"{gov.Tf}",
        "TG",
        f"{gov.Tg}",
        "TW",
        f"{gov.Tw}",
        "AT",
        f"{gov.At}",
        "DT",
        f"{gov.Dturb}",
        "QNL",
        f"{gov.qnl}",
        "Gmin",
        f"{gov.Gmin}",
        "Gmax",
        f"{gov.Gmax}",
        "Velm",
        f"{gov.Velm}",
        nargout=0,
    )
