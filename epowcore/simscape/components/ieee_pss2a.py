import matlab.engine
from epowcore.gdf.power_system_stabilizers.ieee_pss2a import IEEEPSS2A
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.IEEEPSS2A


def create_ieee_pss2a(
    eng: matlab.engine.MatlabEngine, pss: IEEEPSS2A, model_name: str
) -> SimscapeBlock:
    """Create a Simscape block for the IEEEPSS2A power system stabilizer."""

    block_name = f"{model_name}/{pss.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)
    set_parameters_ieee_pss2a(eng, pss, block_name)

    return SimscapeBlock(block_name, BLOCK_TYPE)


def set_parameters_ieee_pss2a(
    eng: matlab.engine.MatlabEngine, pss: IEEEPSS2A, block_name: str
) -> None:
    """Set the parameter values of an existing Simscape block."""

    eng.set_param(
        block_name,
        "K_S1",
        f"{pss.Ks1}",
        "K_S2",
        f"{pss.Ks2}",
        "K_S3",
        f"{pss.Ks3}",
        "T_w1",
        f"{pss.Tw1}",
        "T_w2",
        f"{pss.Tw2}",
        "T_w3",
        f"{pss.Tw3}",
        "T_w4",
        f"{pss.Tw4}",
        "T_1",
        f"{pss.Ts1}",
        "T_2",
        f"{pss.Ts2}",
        "T_3",
        f"{pss.Ts3}",
        "T_4",
        f"{pss.Ts4}",
        "T_6",
        f"{pss.T6}",
        "T_7",
        f"{pss.T7}",
        "T_8",
        f"{pss.T8}",
        "T_9",
        f"{pss.T9}",
        "M",
        f"{pss.M}",
        "N",
        f"{pss.N}",
        "V_STmin",
        f"{pss.Vst_min}",
        "V_STmax",
        f"{pss.Vst_max}",
        # Not modeled in GDF
        "V_SI1max",
        "10",
        "V_SI1min",
        "-10",
        "V_SI2max",
        "10",
        "V_SI2min",
        "-10",
        "P_PSSon",
        "0",
        "P_PSSoff",
        "0",
        "Ts",
        "-1",
        # Not part of PSS2A but PSS2C
        "T_10",
        "0",
        "T_11",
        "0",
        "T_12",
        "0",
        "T_13",
        "0",
        nargout=0,
    )
