import matlab.engine
from epowcore.gdf.governors.ieee_g1 import IEEEG1
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.IEEEG1


def create_ieee_g1(
    eng: matlab.engine.MatlabEngine, gov: IEEEG1, model_name: str
) -> SimscapeBlock:
    """Create a Simscape block for the IEEEG1 governor."""

    block_name = f"{model_name}/{gov.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)
    set_parameters_ieeeg1(eng, gov, block_name)

    return SimscapeBlock(block_name, BLOCK_TYPE)


def set_parameters_ieeeg1(eng: matlab.engine.MatlabEngine, ieeeg1: IEEEG1, block_name: str) -> None:
    """Set the parameter values of an existing Simscape block."""

    eng.set_param(
        block_name,
        "pu_speed_reference",
        "1",
        "pu_torque0",
        "0.45",
        "Ts",
        "-1",
        "K",
        f"{ieeeg1.K}",
        "T_1",
        f"{ieeeg1.T1}",
        "T_2",
        f"{ieeeg1.T2}",
        "T_3",
        f"{ieeeg1.T3}",
        "U_o",
        f"{ieeeg1.Uo}",
        "U_c",
        f"{ieeeg1.Uc}",
        "P_max",
        f"{ieeeg1.Pmax}",
        "P_min",
        f"{ieeeg1.Pmin}",
        "T_4",
        f"{ieeeg1.T4}",
        "K_1",
        f"{ieeeg1.K1}",
        "K_2",
        f"{ieeeg1.K2}",
        "T_5",
        f"{ieeeg1.T5}",
        "K_3",
        f"{ieeeg1.K3}",
        "K_4",
        f"{ieeeg1.K4}",
        "T_6",
        f"{ieeeg1.T6}",
        "K_5",
        f"{ieeeg1.K5}",
        "K_6",
        f"{ieeeg1.K6}",
        "T_7",
        f"{ieeeg1.T7}",
        "K_7",
        f"{ieeeg1.K7}",
        "K_8",
        f"{ieeeg1.K8}",
        "db1",
        f"{ieeeg1.db}",
        nargout=0,
    )
