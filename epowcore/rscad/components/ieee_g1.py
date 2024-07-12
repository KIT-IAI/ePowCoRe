import pyapi_rts.generated.rtdsIEEEG1def as rscadIEEEG1
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.governors.ieee_g1 import IEEEG1
from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


class RSCADIEEEG1(RSCADComponentBuilder):
    @classmethod
    def get_connection_point(
        cls, component: rscadIEEEG1.rtdsIEEEG1def, connection: str
    ) -> tuple[int, int]:
        points = component.connection_points.get(connection)
        if points is None:
            raise ValueError(f"Connection point {connection} not found")
        return points.position_abs

    @classmethod
    def create(  # type: ignore[override]
        cls, component: IEEEG1, base_frequency: float, generator: SynchronousMachine
    ) -> rscadIEEEG1.rtdsIEEEG1def:
        """Creates a RSCAD IEEEG1 governor from a core model IEEEG1 governor element and sets the available values and sets the generator name"""
        rscad_governor = rscadIEEEG1.rtdsIEEEG1def()
        rscad_governor.CONFIGURATION.HTZ.value = base_frequency
        rscad_governor.GOVERNORTURBINEPARAMETERS.K.value = component.K
        rscad_governor.GOVERNORTURBINEPARAMETERS.T1.value = component.T1
        rscad_governor.GOVERNORTURBINEPARAMETERS.T2.value = component.T2
        rscad_governor.GOVERNORTURBINEPARAMETERS.T3.value = component.T3
        rscad_governor.GOVERNORTURBINEPARAMETERS.K1.value = component.K1
        rscad_governor.GOVERNORTURBINEPARAMETERS.K2.value = component.K2
        rscad_governor.GOVERNORTURBINEPARAMETERS.T5.value = component.T5
        rscad_governor.GOVERNORTURBINEPARAMETERS.K3.value = component.K3
        rscad_governor.GOVERNORTURBINEPARAMETERS.K4.value = component.K4
        rscad_governor.GOVERNORTURBINEPARAMETERS.T6.value = component.T6
        rscad_governor.GOVERNORTURBINEPARAMETERS.T4.value = component.T4
        rscad_governor.GOVERNORTURBINEPARAMETERS.K5.value = component.K5
        rscad_governor.GOVERNORTURBINEPARAMETERS.K6.value = component.K6
        rscad_governor.GOVERNORTURBINEPARAMETERS.T7.value = component.T7
        rscad_governor.GOVERNORTURBINEPARAMETERS.K7.value = component.K7
        rscad_governor.GOVERNORTURBINEPARAMETERS.K8.value = component.K8
        rscad_governor.GOVERNORTURBINEPARAMETERS.Uc.value = component.Uc
        rscad_governor.GOVERNORTURBINEPARAMETERS.Pmn.value = component.Pmin
        rscad_governor.GOVERNORTURBINEPARAMETERS.Uo.value = component.Uo
        rscad_governor.GOVERNORTURBINEPARAMETERS.Pmx.value = component.Pmax
        rscad_governor.CONFIGURATION.Ghp.value = RSCADComponentBuilder.sanitize_string(
            generator.name
        )
        return rscad_governor
