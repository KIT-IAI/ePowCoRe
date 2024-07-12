import powerfactory as pf

from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.transformer import WindingConfig
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.power_factory.utils import get_coords


WINDING_CONFIG_MAPPING = {
    "Y": WindingConfig.Y,
    "YN": WindingConfig.YN,
    "Z": WindingConfig.Z,
    "ZN": WindingConfig.ZN,
    "D": WindingConfig.D,
}


def create_three_wdg_trafo(pf_transformer: pf.DataObject, uid: int) -> ThreeWindingTransformer:
    """Sets the attributes from a PowerFactory two winding transformer"""

    rating_hv = pf_transformer.typ_id.strn3_h

    return ThreeWindingTransformer(
        uid,
        pf_transformer.loc_name,
        get_coords(pf_transformer),
        rating_hv=rating_hv,
        rating_mv=pf_transformer.typ_id.strn3_m,
        rating_lv=pf_transformer.typ_id.strn3_l,
        voltage_hv=pf_transformer.typ_id.utrn3_h,
        voltage_mv=pf_transformer.typ_id.utrn3_m,
        voltage_lv=pf_transformer.typ_id.utrn3_l,
        x1_hm=pf_transformer.typ_id.x1pu_h,
        x1_ml=pf_transformer.typ_id.x1pu_m,
        x1_lh=pf_transformer.typ_id.x1pu_l,
        r1_hm=pf_transformer.typ_id.r1pu_h,
        r1_ml=pf_transformer.typ_id.r1pu_m,
        r1_lh=pf_transformer.typ_id.r1pu_l,
        pfe_kw=pf_transformer.typ_id.pfe,
        no_load_current=pf_transformer.typ_id.curm3,
        connection_type_hv=WINDING_CONFIG_MAPPING[pf_transformer.typ_id.tr3cn_h],
        connection_type_mv=WINDING_CONFIG_MAPPING[pf_transformer.typ_id.tr3cn_m],
        connection_type_lv=WINDING_CONFIG_MAPPING[pf_transformer.typ_id.tr3cn_l],
        phase_shift_30_hv=pf_transformer.typ_id.nt3ag_h,
        phase_shift_30_mv=pf_transformer.typ_id.nt3ag_m,
        phase_shift_30_lv=pf_transformer.typ_id.nt3ag_l,
    )


def create_two_wdg_trafo(pf_transformer: pf.DataObject, uid: int) -> TwoWindingTransformer:
    """Sets the attributes from a PowerFactory two winding transformer"""

    rating = pf_transformer.typ_id.strn * pf_transformer.ntnum

    return TwoWindingTransformer(
        uid,
        pf_transformer.loc_name,
        get_coords(pf_transformer),
        rating=rating,
        voltage_hv=pf_transformer.typ_id.utrn_h,
        voltage_lv=pf_transformer.typ_id.utrn_l,
        r1pu=pf_transformer.typ_id.r1pu,
        x1pu=pf_transformer.typ_id.x1pu,
        pfe_kw=pf_transformer.typ_id.pfe,
        no_load_current=pf_transformer.typ_id.curmg,
        connection_type_hv=WINDING_CONFIG_MAPPING[pf_transformer.typ_id.tr2cn_h],
        connection_type_lv=WINDING_CONFIG_MAPPING[pf_transformer.typ_id.tr2cn_l],
        phase_shift_30=pf_transformer.typ_id.nt2ag,
        tap_changer_voltage=pf_transformer.typ_id.dutap / 100,
        tap_min=pf_transformer.typ_id.ntpmn,
        tap_max=pf_transformer.typ_id.ntpmx,
        tap_neutral=pf_transformer.typ_id.nntap0,
        tap_initial=pf_transformer.nntap,
    )
