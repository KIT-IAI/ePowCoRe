import powerfactory as pf
from epowcore.gdf.exciters import Exciter
from epowcore.gdf.exciters.ieee_st1a import IEEEST1A
from epowcore.gdf.exciters.sexs import SEXS
from epowcore.gdf.exciters.ieee_t1 import IEEET1


def create_exciter(self, exciter: Exciter, parent: pf.DataObject = None) -> pf.DataObject:
    match exciter:
        case IEEEST1A():
            return create_ieee_st1a(self, exciter, parent)
        case IEEET1():
            return create_ieee_t1(self, exciter, parent)
        case SEXS():
            return create_sexs(self, exciter, parent)


def create_ieee_st1a(self, exciter: IEEEST1A, parent: pf.DataObject) -> pf.DataObject:
    if parent is None:
        pf_exciter = self.pf_grid.CreateObject("ElmDsl")
    else:
        pf_exciter = parent.CreateObject("ElmDsl")

    pf_exciter_type = self.pf_digsilent_library.GetContents("exc_IEEE_ST1A.BlkDef", 1)[0]
    pf_exciter.SetAttribute("typ_id", pf_exciter_type)

    params = [
        exciter.Ka,
        exciter.Ta,
        exciter.Tb,
        exciter.Tc,
        exciter.Tb1,
        exciter.Tc1,
        exciter.Kf,
        exciter.Tf,
        exciter.Kc,
        exciter.Klr,
        exciter.Ilr,
        exciter.Vs,
        exciter.Vuel,
        exciter.Vi_min,
        exciter.Va_min,
        exciter.Vr_min,
        exciter.Vi_max,
        exciter.Va_max,
        exciter.Vr_max,
    ]
    pf_exciter.SetAttribute("params", params)
    return pf_exciter


def create_ieee_t1(self, exciter: IEEET1, parent: pf.DataObject) -> pf.DataObject:
    raise NotImplementedError


def create_sexs(self, exciter: SEXS, parent: pf.DataObject) -> pf.DataObject:
    raise NotImplementedError
