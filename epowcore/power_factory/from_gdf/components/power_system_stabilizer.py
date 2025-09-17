import powerfactory as pf
from epowcore.gdf.power_system_stabilizers.power_system_stabilizer import PowerSystemStabilizer
from epowcore.gdf.power_system_stabilizers.ieee_pss1a import IEEEPSS1A, PSS1AInputSelector
from epowcore.gdf.power_system_stabilizers.ieee_pss2a import IEEEPSS2A
from epowcore.gdf.power_system_stabilizers.ptist1 import PTIST1


def create_pss(self, pss: PowerSystemStabilizer, parent: pf.DataObject = None) -> pf.DataObject:
    match pss:
        case IEEEPSS1A():
            return create_ieee_pss1a(self, pss, parent)
        case IEEEPSS2A():
            return create_ieee_pss2a(self, pss, parent)
        case PTIST1():
            return create_ptist1(self, pss, parent)


def create_ieee_pss1a(self, pss: IEEEPSS1A, parent: pf.DataObject) -> pf.DataObject:
    if parent is None:
        pf_pss = self.pf_grid.CreateObject("ElmDsl")
    else:
        pf_pss = parent.CreateObject("ElmDsl")

    pf_pss_type = self.pf_digsilent_library.GetContents("pss_IEEE_PSS1A.BlkDef", 1)[0]
    pf_pss.SetAttribute("typ_id", pf_pss_type)
    vsi_in_dict = {
        PSS1AInputSelector.P_GEN: 0,
        PSS1AInputSelector.W: 1,
        PSS1AInputSelector.W_DEV: 2,
        PSS1AInputSelector.F: 3,
        PSS1AInputSelector.F_DEV: 4,
    }
    params = [
        vsi_in_dict[pss.Vsi_in],
        pss.Ks,
        pss.A1,
        pss.A2,
        pss.T1,
        pss.T2,
        pss.T3,
        pss.T4,
        pss.T5,
        pss.T6,
        pss.Vst_min,
        pss.Vst_max,
    ]
    pf_pss.SetAttribute("params", params)
    return pf_pss


def create_ieee_pss2a(self, exciter: IEEEPSS2A, parent: pf.DataObject) -> pf.DataObject:
    raise NotImplementedError


def create_ptist1(self, exciter: PTIST1, parent: pf.DataObject) -> pf.DataObject:
    raise NotImplementedError
