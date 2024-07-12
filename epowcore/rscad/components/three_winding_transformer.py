from pyapi_rts.generated.enums.Noyes2EnumParameter import Noyes2Enum
from pyapi_rts.generated.rtds3P3WTRFdef import rtds3P3WTRFdef
from pyapi_rts.generated.enums.Yd11EnumParameter import Yd11Enum

from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


class RSCAD3WTransformer(RSCADComponentBuilder):
    """Transformer builder for 3 phase 3 winding transformers"""

    @classmethod
    def get_connection_point(
        cls, component: rtds3P3WTRFdef, connection: str
    ) -> tuple[int, int]:
        point = None
        if connection == "HV":
            point = component.connection_points.get("A_1")
        if connection == "MV":
            point = component.connection_points.get("A_2")
        if connection == "LV":
            point = component.connection_points.get("A_3")
        if point is None:
            raise ValueError(
                f"Connection name is not mapped to connection point: {connection}"
            )
        return point.position_abs

    @classmethod
    def create(
        cls, component: ThreeWindingTransformer, base_frequency: float  # type: ignore[override]
    ) -> rtds3P3WTRFdef:
        """Creates a RSCAD 3 phase 3-winding transformer from a datastructure element and sets the available values"""
        r3p3w_transformer = rtds3P3WTRFdef()
        # TODO: Missing: Which value is positive reactance, Connection type for High/Low-Voltage side
        r3p3w_transformer = rtds3P3WTRFdef()
        # Enable connections for third winding
        r3p3w_transformer.CONFIGURATION.n3w.value = Noyes2Enum.Yes
        r3p3w_transformer.CONFIGURATION.Name.value = (
            RSCADComponentBuilder.sanitize_string(component.name)
        )
        r3p3w_transformer.CONFIGURATION.Tmva.value = component.rating_hv
        r3p3w_transformer.WINDING1.V1.value = component.voltage_hv
        r3p3w_transformer.WINDING2.V2.value = component.voltage_lv
        r3p3w_transformer.WINDING3.V3.value = component.voltage_mv
        r3p3w_transformer.CONFIGURATION.r12.value = component.r1_lh
        r3p3w_transformer.CONFIGURATION.r23.value = component.r1_ml
        r3p3w_transformer.CONFIGURATION.r13.value = component.r1_hm
        r3p3w_transformer.CONFIGURATION.nll.value = component.pfe_pu
        r3p3w_transformer.WINDING1.Im1.value = component.no_load_current
        r3p3w_transformer.WINDING2.Im2.value = component.no_load_current
        r3p3w_transformer.CONFIGURATION.f.value = base_frequency
        # TODO: This depends on the winding pairs, no information from PowerFactory
        # r3P3WTransformer.CONFIGURATION.xl.value = transformer3W.positiveReactance)
        # TODO: Needs to be decided by the information from the dataStructure
        r3p3w_transformer.WINDING1.YD1_3W.value = Yd11Enum.Y
        r3p3w_transformer.WINDING2.YD2_3W.value = Yd11Enum.Y
        r3p3w_transformer.WINDING3.YD3_3W.value = Yd11Enum.Y
        return r3p3w_transformer
