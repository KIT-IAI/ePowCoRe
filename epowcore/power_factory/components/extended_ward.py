import powerfactory as pf

from epowcore.gdf.extended_ward import ExtendedWard
from epowcore.power_factory.utils import get_coords


def create_extended_ward(pf_ward: pf.DataObject, uid: int) -> ExtendedWard:
    """Create a Ward equivalent from a PowerFactory DataObject."""

    return ExtendedWard(
        uid,
        name=pf_ward.loc_name,
        coords=get_coords(pf_ward),
        p_load=pf_ward.Pload,
        q_load=pf_ward.Qload,
        p_gen=pf_ward.Pgen,
        q_gen=pf_ward.Qgen,
        p_zload=pf_ward.Pzload,
        q_zload=pf_ward.Qzload,
        u_setp=pf_ward.usetp,
        r_ext=pf_ward.Rext,
        x_ext=pf_ward.Xext,
    )
