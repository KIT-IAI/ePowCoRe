import powerfactory as pf
from epowcore.gdf.governors import Governor
from epowcore.gdf.governors.ieee_g1 import IEEEG1
from epowcore.gdf.governors.hygov import HYGOV
from epowcore.gdf.governors.gast import GAST


def create_governor(self, governor: Governor, parent: pf.DataObject = None) -> pf.DataObject:
    match governor:
        case IEEEG1():
            return create_ieee_g1(self, governor, parent)
        case HYGOV():
            return create_hygov(self, governor, parent)
        case GAST():
            return create_gast(self, governor, parent)
        
def create_ieee_g1(self, governor: IEEEG1, parent: pf.DataObject) -> pf.DataObject:
    if parent is None:
        pf_governor = self.pf_grid.CreateObject("ElmDsl")
    else:
        pf_governor = parent.CreateObject("ElmDsl")
    
    pf_governor_type = self.pf_digsilent_library.GetContents("gov_IEEE_IEEEG1.BlkDef", 1)[0]
    pf_governor.SetAttribute("typ_id", pf_governor_type)
    params = [
        governor.PNhp,
        governor.PNlp,
        governor.K,
        governor.T1,
        governor.T2,
        governor.T3,
        governor.T4,
        governor.K1,
        governor.K2,
        governor.T5,
        governor.K3,
        governor.K4,
        governor.T6,
        governor.K5,
        governor.K6,
        governor.T7,
        governor.K7,
        governor.K8,
        governor.db,
        governor.Uc,
        governor.Pmin,
        governor.Uo,
        governor.Pmax
    ]
    pf_governor.SetAttribute("params", params)
    return pf_governor


def create_hygov(self, governor: HYGOV, parent: pf.DataObject) -> pf.DataObject:
    raise NotImplementedError

def create_gast(self, governor: GAST, parent: pf.DataObject) -> pf.DataObject:
    raise NotImplementedError
