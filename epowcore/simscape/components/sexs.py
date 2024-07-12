import matlab.engine
from epowcore.gdf.exciters.sexs import SEXS
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType


BLOCK_TYPE = SimscapeBlockType.SEXS


def create_sexs(eng: matlab.engine.MatlabEngine, exc: SEXS, model_name: str) -> SimscapeBlock:
    """Create a Simscape block for the SEXS exciter."""
    block_name = f"{model_name}/{exc.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)

    set_parameters_sexs(eng, exc, block_name)

    return SimscapeBlock(block_name, BLOCK_TYPE)


def set_parameters_sexs(eng: matlab.engine.MatlabEngine, exc: SEXS, block_name: str) -> None:
    """Set the parameter values of an existing Simscape block."""

    eng.set_param(
        block_name,
        "TA",
        f"{exc.Ta}",
        "TB",
        f"{exc.Tb}",
        "K",
        f"{exc.K}",
        "TE",
        f"{exc.Te}",
        "Emin",
        f"{exc.Emin}",
        "Emax",
        f"{exc.Emax}",
        nargout=0,
    )
