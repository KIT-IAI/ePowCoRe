import powerfactory as pf

from epowcore.gdf.ward import Ward
from epowcore.power_factory.utils import get_coords


def create_ward(pf_ward: pf.DataObject, uid: int) -> Ward:
    """Create a Ward equivalent from a PowerFactory DataObject."""

    return Ward(
        uid=uid,
        name=pf_ward.loc_name,
        coords=get_coords(pf_ward),
        p_load=pf_ward.Pload,
        q_load=pf_ward.Qload,
        p_gen=pf_ward.Pgen,
        q_gen=pf_ward.Qgen,
        p_zload=pf_ward.Pzload,
        q_zload=pf_ward.Qzload,
    )
