import powerfactory as pf

from epowcore.gdf.shunt import Shunt


def create_shunt(
    pf_shunt: pf.DataObject,
    uid: int,
    use_load_flow: bool = False,
) -> Shunt:
    """Create a shunt from a PowerFactory shunt object."""

    q = (
        pf_shunt.GetAttribute("e:Qact")
        if use_load_flow
        else pf_shunt.GetAttribute("qcapn")
    )

    return Shunt(
        uid=uid,
        name=pf_shunt.loc_name,
        p=0.0,
        q=q,
    )