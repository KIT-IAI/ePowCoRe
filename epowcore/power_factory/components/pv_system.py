import powerfactory as pf

from epowcore.gdf.pv_system import PVSystem
from epowcore.power_factory.utils import get_coords


def create_pv_system(pf_pv_system: pf.DataObject, uid: int) -> PVSystem:
    """Sets the attributes of PVSystem from a PowerFactory PV system"""

    # ngnum = pfPvSystem.ngnum

    return PVSystem(
        uid,
        pf_pv_system.loc_name,
        get_coords(pf_pv_system),
        rated_power=pf_pv_system.sgn / 1000,
        real_power_output=pf_pv_system.pgini / 1000,
        reactive_power_output=pf_pv_system.qgini / 1000,
        minimum_real_power_output=pf_pv_system.Pmin_a / 1000,
        maximum_real_power_output=pf_pv_system.Pmax_a / 1000,
        minimum_reactive_power_output=pf_pv_system.Pmin_a / 1000,
        maximum_reactive_power_output=pf_pv_system.Pmax_a / 1000,
    )
