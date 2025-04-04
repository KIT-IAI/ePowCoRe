import powerfactory as pf

from epowcore.gdf.shunt import Shunt


def create_shunt(pf_shunt: pf.DataObject, uid: int) -> Shunt:
    """Create a shunt from a PowerFactory shunt object."""

    return Shunt(
        uid=uid,
        name=pf_shunt.loc_name,
        p=0.0,
        q=pf_shunt.GetAttribute("e:Qact"),
    )
