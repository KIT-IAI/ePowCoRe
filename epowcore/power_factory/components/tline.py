import powerfactory as pf

from epowcore.gdf.tline import TLine
from epowcore.power_factory.utils import get_coords


def create_tline(pf_tline: pf.DataObject, uid: int) -> TLine:
    """Set the attributes of TLine from a Pf transmission line"""

    rating = pf_tline.typ_id.uline * pf_tline.typ_id.sline

    # if zero sequence data is 0, consider it as not modeled
    r0 = pf_tline.typ_id.rline0 if pf_tline.typ_id.rline0 != 0 else None
    x0 = pf_tline.typ_id.xline0 if pf_tline.typ_id.xline0 != 0 else None
    b0 = pf_tline.typ_id.bline0 if pf_tline.typ_id.bline0 != 0 else None

    return TLine(
        uid,
        pf_tline.loc_name,
        coords=get_coords(pf_tline),
        length=pf_tline.dline,
        r1=pf_tline.typ_id.rline,
        x1=pf_tline.typ_id.xline,
        b1=pf_tline.typ_id.bline,
        r0=r0,
        x0=x0,
        b0=b0,
        rating=rating,
        parallel_lines=pf_tline.nlnum,
    )
