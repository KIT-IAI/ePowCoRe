from pyapi_rts.generated.enums.EdgeEnumParameter import EdgeEnum
from pyapi_rts.generated.enums.Yd1EnumParameter import Yd1Enum
from pyapi_rts.generated.rtds3P2WTRFdef import rtds3P2WTRFdef

from epowcore.gdf.transformers import TwoWindingTransformer
from epowcore.gdf.transformers.transformer import WindingConfig
from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


class RSCAD2WTransformer(RSCADComponentBuilder):
    @classmethod
    def get_connection_point(
        cls, component: rtds3P2WTRFdef, connection: str
    ) -> tuple[int, int]:
        point = None
        if connection == "HV":
            point = component.connection_points.get("A_1")
        if connection == "LV":
            point = component.connection_points.get("A_2")
        if point is None:
            raise ValueError(
                f"Connection name is not mapped to connection point: {connection}"
            )
        return point.position_abs

    @classmethod
    def create(
        cls, component: TwoWindingTransformer, base_frequency: float  # type: ignore[override]
    ) -> rtds3P2WTRFdef:
        """Create an RSCAD 3 phase 2-winding transformer from a core model 
        TwoWindingTransformer component and set the available values.
        """
        r3p2w_transformer = rtds3P2WTRFdef()
        r3p2w_transformer.CONFIGURATION.Name.value = cls.sanitize_string(component.name)
        r3p2w_transformer.CONFIGURATION.Tmva.value = component.rating
        r3p2w_transformer.CONFIGURATION.edge.value = EdgeEnum.Rising_Edge
        r3p2w_transformer.CONFIGURATION.CuL.value = component.r1pu
        r3p2w_transformer.CONFIGURATION.NLL.value = component.pfe_pu
        r3p2w_transformer.CONFIGURATION.f.value = base_frequency
        r3p2w_transformer.CONFIGURATION.xl.value = component.x1pu

        r3p2w_transformer.WINDING1.VL1.value = component.voltage_hv
        r3p2w_transformer.WINDING1.Im1.value = component.no_load_current
        r3p2w_transformer.WINDING1.YD1.value = Yd1Enum.Y_Gnd
        
        r3p2w_transformer.WINDING2.VL2.value = component.voltage_lv
        r3p2w_transformer.WINDING2.Im2.value = component.no_load_current
        r3p2w_transformer.WINDING2.YD2.value = Yd1Enum.Y_Gnd
        # Set tap changer values
        # TODO: Check if tap changer needs to be set, setting it causes value dicrepancies with the IEEE14/39 test cases
        tap_details = component.get_tap_details_fb()
        tap_count = abs(tap_details.tap_max) + abs(tap_details.tap_min) + 1
        tap_neutral = tap_count - abs(tap_details.tap_min)
        # TODO: This only works if the tap neutral is the middle value of tap positions
        tap_starting = tap_neutral + tap_details.tap_initial
        # r3P2WTransformer.CONFIGURATION.tapCh.value = TapchEnum.Pos_Table)
        r3p2w_transformer.TAPCHANGERA.NoTaps.value = tap_count
        r3p2w_transformer.TAPCHANGERA.TR1.value = tap_starting
        for x in range(1, tap_count + 1):
            r3p2w_transformer.set_by_key(
                f"P{x}", 1.00 + (x - tap_neutral) * tap_details.tap_changer_voltage
            )

        # Currently set the voltage directly at the high voltage side instead of using a tap changer
        r3p2w_transformer.WINDING1.VL1.value = component.voltage_hv * (
            1.00 + (tap_starting - tap_neutral) * tap_details.tap_changer_voltage
        )
        # TODO: Commented out at parts the moment, to compile the case for other options than YGround or Delta
        # Impedances at the connections are needed
        if component.connection_type_hv_fb == WindingConfig.D:
            r3p2w_transformer.WINDING1.YD1.value = Yd1Enum.Delta
        # elif transformer2W.connectionTypeHighVoltage  == "Z" or "ZN":
        #     r3P2WTransformer.WINDING1.YD1.value = rscad2WTransformerConnectionEnum.Yd1Enum.Y_ZY_Z)
        # else:
        #     r3P2WTransformer.WINDING1.YD1.value = rscad2WTransformerConnectionEnum.Yd1Enum.Y_GndY_Gnd)

        if component.connection_type_lv_fb == WindingConfig.D:
            r3p2w_transformer.WINDING2.YD2.value = Yd1Enum.Delta
        # elif transformer2W.connectionTypeLowVoltage  == "Z" or "ZN":
        #     r3P2WTransformer.WINDING2.YD2.value = rscad2WTransformerConnectionEnum.Yd1Enum.Y_ZY_Z)
        # else:
        #     r3P2WTransformer.WINDING2.YD2.value = rscad2WTransformerConnectionEnum.Yd1Enum.Y_GndY_Gnd)
        return r3p2w_transformer
