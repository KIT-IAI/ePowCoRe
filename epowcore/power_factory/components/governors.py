import powerfactory as pf

from epowcore.gdf.governors.gast import GAST
from epowcore.gdf.governors.hygov import HYGOV
from epowcore.gdf.governors.ieee_g1 import IEEEG1
from epowcore.power_factory.utils import get_coords, get_ctrl_param


def create_ieee_g1(gov: pf.DataObject, uid: int) -> IEEEG1:
    """Create IEEE G1 governor from PowerFactory gov object."""

    try:
        db = get_ctrl_param(gov, "db")
    except ValueError:
        db = 0

    return IEEEG1(
        uid,
        gov.loc_name,
        get_coords(gov),
        K=get_ctrl_param(gov, "K"),
        T1=get_ctrl_param(gov, "T1"),
        T2=get_ctrl_param(gov, "T2"),
        T3=get_ctrl_param(gov, "T3"),
        K1=get_ctrl_param(gov, "K1"),
        K2=get_ctrl_param(gov, "K2"),
        T5=get_ctrl_param(gov, "T5"),
        K3=get_ctrl_param(gov, "K3"),
        K4=get_ctrl_param(gov, "K4"),
        T6=get_ctrl_param(gov, "T6"),
        K5=get_ctrl_param(gov, "K5"),
        K6=get_ctrl_param(gov, "K6"),
        T4=get_ctrl_param(gov, "T4"),
        T7=get_ctrl_param(gov, "T7"),
        K7=get_ctrl_param(gov, "K7"),
        K8=get_ctrl_param(gov, "K8"),
        Uc=get_ctrl_param(gov, "Uc"),
        Pmin=get_ctrl_param(gov, "Pmin"),
        Uo=get_ctrl_param(gov, "Uo"),
        Pmax=get_ctrl_param(gov, "Pmax"),
        db=db,
        PNhp=get_ctrl_param(gov, ["PNhp", "Trate1"]),
        PNlp=get_ctrl_param(gov, ["PNlp", "Trate2"]),
    )


def create_gast(gov: pf.DataObject, uid: int) -> GAST:
    """Create GAST governor from PowerFactory gov object."""

    return GAST(
        uid,
        gov.loc_name,
        get_coords(gov),
        R=get_ctrl_param(gov, "R"),
        T1=get_ctrl_param(gov, "T1"),
        T2=get_ctrl_param(gov, "T2"),
        T3=get_ctrl_param(gov, "T3"),
        AT=get_ctrl_param(gov, "AT"),
        KT=get_ctrl_param(gov, "Kt"),
        Vmin=get_ctrl_param(gov, "Vmin"),
        Vmax=get_ctrl_param(gov, "Vmax"),
        Dturb=get_ctrl_param(gov, "Dturb"),
    )


def create_hygov(gov: pf.DataObject, uid: int) -> HYGOV:
    """Create HYGOV governor from PowerFactory gov object."""

    return HYGOV(
        uid,
        gov.loc_name,
        get_coords(gov),
        R_temp=get_ctrl_param(gov, "r"),
        R_perm=get_ctrl_param(gov, "R"),
        Tr=get_ctrl_param(gov, "Tr"),
        Tf=get_ctrl_param(gov, "Tf"),
        Tg=get_ctrl_param(gov, "Tg"),
        Tw=get_ctrl_param(gov, "Tw"),
        At=get_ctrl_param(gov, "At"),
        Dturb=get_ctrl_param(gov, "Dturb"),
        qnl=get_ctrl_param(gov, "qnl"),
        Gmin=get_ctrl_param(gov, "Gmin"),
        Gmax=get_ctrl_param(gov, "Gmax"),
        Velm=get_ctrl_param(gov, "Velm"),
    )
