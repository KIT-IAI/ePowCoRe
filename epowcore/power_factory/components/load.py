from math import acos, tan
import powerfactory as pf

from epowcore.gdf.load import Load
from epowcore.power_factory.utils import get_coords


def create_load(pf_load: pf.DataObject, uid: int) -> Load:
    """Sets the attributes of Load from a PowerFactory load"""

    return Load(
        uid,
        pf_load.loc_name,
        get_coords(pf_load),
        active_power=pf_load.plini,
        reactive_power=pf_load.qlini,
    )


def create_load_lv(pf_load: pf.DataObject, uid: int) -> Load:
    """Sets the attributes of Load from a PowerFactory load"""

    active_power = pf_load.plini_a / 1000

    return Load(
        uid,
        pf_load.loc_name,
        get_coords(pf_load),
        active_power=active_power,
        reactive_power=active_power * tan(acos(pf_load.coslini_a)),
    )
