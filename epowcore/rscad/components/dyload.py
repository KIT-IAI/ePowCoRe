import logging
import pyapi_rts.generated.rtdsudcDYLOAD as rdyLoad
from pyapi_rts.generated.enums.Type30EnumParameter import Type30Enum
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.load import Load

from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


class RSCADDyload(RSCADComponentBuilder):
    @classmethod
    def get_connection_point(
        cls, component: rdyLoad.rtdsudcDYLOAD, connection: str
    ) -> tuple[int, int]:
        a1 = component.connection_points.get("A_1")
        if a1 is None:
            raise ValueError(
                f"Connection point A_1 not found in {component.name} {component.type}"
            )
        return a1.position_abs

    @classmethod
    def create(cls, component: Load, base_frequency: float) -> rdyLoad.rtdsudcDYLOAD:  # type: ignore[override]
        """Creates a RSCAD dyload transformer from a core model load element and sets the available values
        :param base_frequency: The vbus value, not great code but works for now
        """
        rscad_dyload = rdyLoad.rtdsudcDYLOAD()
        # Set attributes
        rscad_dyload.PARAMETERS.Name.value = RSCADComponentBuilder.sanitize_string(
            component.name
        )
        rscad_dyload.PANDQSETTINGS.Pinit.value = component.active_power
        rscad_dyload.PANDQSETTINGS.Qinit.value = component.reactive_power
        # Set the min values to half of init and the max values to double of init
        rscad_dyload.PANDQSETTINGS.Pmax.value = (
            2 * rscad_dyload.PANDQSETTINGS.Pinit.value  # type: ignore
        )
        rscad_dyload.PANDQSETTINGS.Pmin.value = (
            0.5 * rscad_dyload.PANDQSETTINGS.Pinit.value  # type: ignore
        )

        if component.reactive_power > 0.0:
            rscad_dyload.PANDQSETTINGS.Qmax.value = (
                2 * rscad_dyload.PANDQSETTINGS.Qinit.value  # type: ignore
            )
            rscad_dyload.PANDQSETTINGS.Qmin.value = (
                0.5 * rscad_dyload.PANDQSETTINGS.Qinit.value  # type: ignore
            )
        elif component.reactive_power < 0.0:
            # For negative reactive power change type of load and Qmin below Qinit
            rscad_dyload.PARAMETERS.type.value = Type30Enum.RX
            rscad_dyload.PANDQSETTINGS.Qmin.value = component.reactive_power - 1.0
            rscad_dyload.PANDQSETTINGS.Qmax.value = component.reactive_power * (-1)
            logging.info(
                "%s|%s|PARAMETER type: %s, Qmin: %e, Qmax: %e",
                rscad_dyload.type,
                rscad_dyload.name,
                Type30Enum.RX,
                component.reactive_power - 1.0,
                component.reactive_power * (-1),
            )
        else:
            rscad_dyload.PANDQSETTINGS.Qinit.value = 0.001
            rscad_dyload.PANDQSETTINGS.Qmin.value = 0.001
        rscad_dyload.PARAMETERS.Vbus.value = base_frequency
        return rscad_dyload

    @classmethod
    def create_with_vbus_value(
        cls, component: Load, base_frequency: float, generator: SynchronousMachine
    ) -> rdyLoad.rtdsudcDYLOAD:
        rscad_dyload = cls.create(component, base_frequency)
        rscad_dyload.PARAMETERS.Name.value = RSCADComponentBuilder.sanitize_string(
            generator.name
        )
        rscad_dyload.PARAMETERS.Vbus.value = base_frequency
        return rscad_dyload
