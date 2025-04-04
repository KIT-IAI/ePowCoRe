import powerfactory as pf

from epowcore.gdf.exciters.ieee_st1a import IEEEST1A
from epowcore.gdf.exciters.ieee_t1 import IEEET1
from epowcore.gdf.exciters.sexs import SEXS
from epowcore.power_factory.utils import get_coords, get_ctrl_param


def create_ieee_st1a(avr: pf.DataObject, uid: int) -> IEEEST1A:
    """Create IEEE ST1A exciter from PowerFactory avr object."""

    try:
        Tr = get_ctrl_param(avr, "Tr")
    except ValueError:
        Tr = None
        # raise ValueError("Tr is not defined for this exciter type")

    return IEEEST1A(
        uid,
        avr.loc_name,
        get_coords(avr),
        Tr=Tr,
        Ka=get_ctrl_param(avr, "Ka"),
        Ta=get_ctrl_param(avr, "Ta"),
        Tb=get_ctrl_param(avr, "Tb"),
        Tc=get_ctrl_param(avr, "Tc"),
        Tb1=get_ctrl_param(avr, "Tb1"),
        Tc1=get_ctrl_param(avr, "Tc1"),
        Kf=get_ctrl_param(avr, "Kf"),
        Tf=get_ctrl_param(avr, "Tf"),
        Kc=get_ctrl_param(avr, "Kc"),
        Klr=get_ctrl_param(avr, "Klr"),
        Ilr=get_ctrl_param(avr, "Ilr"),
        Vs=get_ctrl_param(avr, ["Vs_in", "Vos"]),
        Vuel=get_ctrl_param(avr, ["Vuel_in", "Vel"]),
        Vi_min=get_ctrl_param(avr, ["Vimin", "Vi_min"]),
        Va_min=get_ctrl_param(avr, ["Vamin", "Va_min"]),
        Vr_min=get_ctrl_param(avr, ["Vrmin", "Vr_min"]),
        Vi_max=get_ctrl_param(avr, ["Vimax", "Vi_max"]),
        Va_max=get_ctrl_param(avr, ["Vamax", "Va_max"]),
        Vr_max=get_ctrl_param(avr, ["Vrmax", "Vr_max"]),
    )


def create_ieee_t1(avr: pf.DataObject, uid: int) -> IEEET1:
    """Create IEEE T1 exciter from PowerFactory avr object."""

    return IEEET1(
        uid,
        avr.loc_name,
        get_coords(avr),
        Tr=avr.params[0],
        Ka=avr.params[1],
        Ta=avr.params[2],
        Ke=avr.params[3],
        Te=avr.params[4],
        Kf=avr.params[5],
        Tf=avr.params[6],
        E1=avr.params[7],
        Se1=avr.params[8],
        E2=avr.params[9],
        Se2=avr.params[10],
        Vrmin=avr.params[11],
        Vrmax=avr.params[12],
    )


def create_sexs(avr: pf.DataObject, uid: int) -> SEXS:
    """Create SEXS exciter from PowerFactory avr object."""

    return SEXS(
        uid,
        avr.loc_name,
        get_coords(avr),
        Ta=get_ctrl_param(avr, "Ta"),
        Tb=get_ctrl_param(avr, "Tb"),
        K=get_ctrl_param(avr, "K"),
        Te=get_ctrl_param(avr, "Te"),
        Emin=get_ctrl_param(avr, "Emin"),
        Emax=get_ctrl_param(avr, "Emax"),
    )
