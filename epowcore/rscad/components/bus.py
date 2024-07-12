import pyapi_rts.generated.rtdssharcsldBUSLABEL as rbus
import pyapi_rts.generated.enums.Type6EnumParameter as rscadBusEnum
from pyapi_rts.generated.enums.Noyes2EnumParameter import Noyes2Enum
from pyapi_rts.api.parameters.connection_point import ConnectionPoint
from epowcore.gdf.bus import Bus

from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder
from epowcore.gdf.bus import LFBusType


class RSCADBus(RSCADComponentBuilder):
    @classmethod
    def get_connection_point(
        cls, component: rbus.rtdssharcsldBUSLABEL, connection: str
    ) -> tuple[int, int]:
        if connection == "A_1":
            a1 = component.connection_points.get("A_1")
            if isinstance(a1, ConnectionPoint):
                return a1.position_abs
        if connection == "A_2":
            a2 = component.connection_points.get("A_2")
            if isinstance(a2, ConnectionPoint):
                return a2.position_abs
        raise ValueError(
            f"Connection name is not mapped to connection point: {connection}"
        )

    @classmethod
    def create(cls, component: Bus, base_frequency: float) -> rbus.rtdssharcsldBUSLABEL:  # type: ignore[override]
        """Creates a RSCAD bus label from a datastructure bus element and sets the available values"""
        rs_bus = rbus.rtdssharcsldBUSLABEL()
        rs_bus.Parameters.BName.value = RSCADComponentBuilder.sanitize_string(
            component.name
        )
        rs_bus.Parameters.sameNames.value = Noyes2Enum.Yes
        rs_bus.Parameters.linkNodes.value = Noyes2Enum.Yes
        rs_bus.Parameters.VRate.value = component.nominal_voltage
        # Set value of the right enum
        if component.lf_bus_type == LFBusType.PQ:
            rs_bus.LOADFLOWDATA.Type.value = rscadBusEnum.Type6Enum.PQ_BUS
        elif component.lf_bus_type == LFBusType.PV:
            rs_bus.LOADFLOWDATA.Type.value = rscadBusEnum.Type6Enum.PV_BUS
        elif component.lf_bus_type == LFBusType.SL:
            rs_bus.LOADFLOWDATA.Type.value = rscadBusEnum.Type6Enum.SLACK
        return rs_bus
