import powerfactory as pf

from epowcore.gdf.switch import Switch
from epowcore.power_factory.utils import get_coords


def create_switch(pf_switch: pf.DataObject, uid: int) -> Switch:
    """Create a Switch from a PF DataObject (ElmCoup)."""
    return Switch(
        uid,
        pf_switch.loc_name,
        coords=get_coords(pf_switch),
        closed=(pf_switch.on_off == 1),
    )
