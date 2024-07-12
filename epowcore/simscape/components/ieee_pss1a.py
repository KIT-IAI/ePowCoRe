import matlab.engine
from epowcore.gdf.power_system_stabilizers.ieee_pss1a import IEEEPSS1A
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.IEEEPSS1A


def create_ieee_pss1a(
    eng: matlab.engine.MatlabEngine, pss: IEEEPSS1A, model_name: str
) -> SimscapeBlock:
    """Create a Simscape block for the IEEEPSS1A power system stabilizer."""

    block_name = f"{model_name}/{pss.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)
    set_parameters_ieee_pss1a(eng, pss, block_name)

    return SimscapeBlock(block_name, BLOCK_TYPE)


def set_parameters_ieee_pss1a(
    eng: matlab.engine.MatlabEngine, pss: IEEEPSS1A, block_name: str
) -> None:
    """Set the parameter values of an existing Simscape block."""

    eng.set_param(
        block_name,
        "K_S",
        f"{pss.Ks}",
        "A_1",
        f"{pss.A1}",
        "A_2",
        f"{pss.A2}",
        "T_1",
        f"{pss.T1}",
        "T_2",
        f"{pss.T2}",
        "T_3",
        f"{pss.T3}",
        "T_4",
        f"{pss.T4}",
        "T_5",
        f"{pss.T5}",
        "T_6",
        f"{pss.T6}",
        "V_STmax",
        f"{pss.Vst_max}",
        "V_STmin",
        f"{pss.Vst_min}",
        "Ts",
        "-1",
        nargout=0,
    )
