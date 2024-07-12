import powerfactory as pf
from epowcore.gdf.common_impedance import CommonImpedance

from epowcore.power_factory.utils import get_coords


def create_impedance(pf_impedance: pf.DataObject, uid: int) -> CommonImpedance:
    """Create an impedance from a PowerFactory DataObject."""

    r_pu_ji = None
    x_pu_ji = None
    if pf_impedance.iequalz == 0:
        r_pu_ji = pf_impedance.r_pu_ji
        x_pu_ji = pf_impedance.x_pu_ji

    return CommonImpedance(
        uid,
        pf_impedance.loc_name,
        get_coords(pf_impedance),
        sn_mva=pf_impedance.Sn,
        r_pu=pf_impedance.r_pu,
        x_pu=pf_impedance.x_pu,
        r_pu_ba=r_pu_ji,
        x_pu_ba=x_pu_ji,
        g_pu_a=pf_impedance.gi_pu,
        b_pu_a=pf_impedance.bi_pu,
        g_pu_b=pf_impedance.gj_pu,
        b_pu_b=pf_impedance.bj_pu,
        phase_shift=pf_impedance.nphshift * 30 + pf_impedance.ag,
    )
