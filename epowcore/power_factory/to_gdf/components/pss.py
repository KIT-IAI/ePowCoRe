import powerfactory as pf

from epowcore.gdf.power_system_stabilizers.ieee_pss1a import IEEEPSS1A, PSS1AInputSelector
from epowcore.gdf.power_system_stabilizers.ieee_pss2a import IEEEPSS2A, PSS2AInputSelector
from epowcore.gdf.power_system_stabilizers.ptist1 import PTIST1
from epowcore.power_factory.utils import get_coords, get_ctrl_param


def create_ieee_pss1a(pss: pf.DataObject, uid: int) -> IEEEPSS1A:
    """Set attributes from the PowerFactory avr"""

    return IEEEPSS1A(
        uid,
        pss.loc_name,
        get_coords(pss),
        Vsi_in=PSS1A_SELECTOR_MAP[get_ctrl_param(pss, "Vsi_in")],
        Ks=get_ctrl_param(pss, "Ks"),
        A1=get_ctrl_param(pss, "A1"),
        A2=get_ctrl_param(pss, "A2"),
        T1=get_ctrl_param(pss, "T1"),
        T2=get_ctrl_param(pss, "T2"),
        T3=get_ctrl_param(pss, "T3"),
        T4=get_ctrl_param(pss, "T4"),
        T5=get_ctrl_param(pss, "T5"),
        T6=get_ctrl_param(pss, "T6"),
        Vst_min=get_ctrl_param(pss, "Vst_min"),
        Vst_max=get_ctrl_param(pss, "Vst_max"),
    )


def create_ieee_pss2a(pss: pf.DataObject, uid: int) -> IEEEPSS2A:
    """Set the attributes from PF PFF"""

    return IEEEPSS2A(
        uid,
        pss.loc_name,
        get_coords(pss),
        In1=PSS2A_SELECTOR_MAP[get_ctrl_param(pss, "Ic1")],
        In2=PSS2A_SELECTOR_MAP[get_ctrl_param(pss, "Ic2")],
        Tw1=get_ctrl_param(pss, "Tw1"),
        Tw2=get_ctrl_param(pss, "Tw2"),
        Tw3=get_ctrl_param(pss, "Tw3"),
        Tw4=get_ctrl_param(pss, "Tw4"),
        T6=get_ctrl_param(pss, "T6"),
        T7=get_ctrl_param(pss, "T7"),
        Ks2=get_ctrl_param(pss, "Ks2"),
        Ks3=get_ctrl_param(pss, "Ks3"),
        T8=get_ctrl_param(pss, "T8"),
        T9=get_ctrl_param(pss, "T9"),
        M=get_ctrl_param(pss, "M"),
        N=get_ctrl_param(pss, "N"),
        Ks1=get_ctrl_param(pss, "Ks1"),
        Ts1=get_ctrl_param(pss, "Ts1"),
        Ts2=get_ctrl_param(pss, "Ts2"),
        Ts3=get_ctrl_param(pss, "Ts3"),
        Ts4=get_ctrl_param(pss, "Ts4"),
        Vst_min=get_ctrl_param(pss, "Vstmin"),
        Vst_max=get_ctrl_param(pss, "Vstmax"),
    )


def create_ptist1(pss: pf.DataObject, uid: int) -> PTIST1:
    """Set the attributes from PF PFF"""

    return PTIST1(
        uid,
        pss.loc_name,
        get_coords(pss),
        Kpss=pss.params[0],
        Tw=pss.params[1],
        T1=pss.params[2],
        T2=pss.params[3],
        T3=pss.params[4],
        T4=pss.params[5],
    )


PSS1A_SELECTOR_MAP = {
    0: PSS1AInputSelector.P_GEN,
    1: PSS1AInputSelector.W,
    2: PSS1AInputSelector.W_DEV,
    3: PSS1AInputSelector.F,
    4: PSS1AInputSelector.F_DEV,
}


PSS2A_SELECTOR_MAP = {
    0: PSS2AInputSelector.NONE,
    1: PSS2AInputSelector.W_DEV,
    2: PSS2AInputSelector.F_DEV,
    3: PSS2AInputSelector.P_GEN_EL,
    4: PSS2AInputSelector.P_GEN_ACC,
    5: PSS2AInputSelector.V_BUS,
    6: PSS2AInputSelector.VD_BUS,
}
