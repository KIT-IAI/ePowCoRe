import matlab.engine
from epowcore.gdf.exciters.ieee_st1a import IEEEST1A
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType
from epowcore.simscape.tools import get_param_in_bounds


BLOCK_TYPE = SimscapeBlockType.IEEEST1A


def create_ieee_st1a(
    eng: matlab.engine.MatlabEngine, exc: IEEEST1A, model_name: str
) -> SimscapeBlock:
    """Create a Simscape block for the IEEEST1A exciter."""
    block_name = f"{model_name}/{exc.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)

    set_parameters_ieee_st1a(eng, exc, block_name)

    return SimscapeBlock(block_name, BLOCK_TYPE)


def set_parameters_ieee_st1a(
    eng: matlab.engine.MatlabEngine, exc: IEEEST1A, block_name: str
) -> None:
    """Set the parameter values of an existing Simscape block."""
    kf = get_param_in_bounds(exc.Kf, 1e-3, 0.3, f"{block_name}.Kf")

    eng.set_param(
        block_name,
        "Tr",
        "20e-3",
        "KaTa",
        f"[{exc.Ka},{exc.Ta}]",
        "VIminmax",
        f"[{exc.Vi_min},{exc.Vi_max}]",
        "VAminmax",
        f"[{exc.Va_min},{exc.Va_max}]",
        "VRminmax",
        f"[{exc.Vr_min},{exc.Vr_max}]",
        "KfTf",
        f"[{kf},{exc.Tf}]",
        "TbTc",
        f"[{exc.Tb},{exc.Tc},{exc.Tb1},{exc.Tc1}]",
        "KLR",
        f"{exc.Klr}",
        "ILR",
        f"{exc.Ilr}",
        "Kc",
        f"{exc.Kc}",
        "v0",
        "[1 1]",
        "TsBlock",
        "0",
        nargout=0,
    )
