import pyapi_rts.generated.rtdsIEEET1def as rscadIEEET1
from epowcore.gdf.exciters.ieee_t1 import IEEET1
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine

from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


class RSCADIEEET1(RSCADComponentBuilder):
    @classmethod
    def get_connection_point(
        cls, component: rscadIEEET1.rtdsIEEET1def, connection: str
    ) -> tuple[int, int]:
        points = component.connection_points.get(connection)
        if points is None:
            raise ValueError(f"Connection point {connection} not found")
        return points.position_abs

    @classmethod
    def create(  # type: ignore[override]
        cls, component: IEEET1, base_frequency: float, generator: SynchronousMachine
    ) -> rscadIEEET1.rtdsIEEET1def:
        """
        Creates a RSCAD ieeeet1 exciter from a datastructure ieeeet1 exciter element and sets the available values, including the generator name from a datastructure generator element
        """
        rs_exciter = rscadIEEET1.rtdsIEEET1def()
        rs_exciter.CONFIGURATION.HTZ.value = base_frequency
        rs_exciter.EXCITERPARAMETERS.Tr.value = component.Tr
        rs_exciter.EXCITERPARAMETERS.Ka.value = component.Ka
        rs_exciter.EXCITERPARAMETERS.Ta.value = component.Ta
        rs_exciter.EXCITERPARAMETERS.Ke.value = component.Ke
        rs_exciter.EXCITERPARAMETERS.Te.value = component.Te
        rs_exciter.EXCITERPARAMETERS.Kf.value = component.Kf
        rs_exciter.EXCITERPARAMETERS.Tf.value = component.Tf
        rs_exciter.EXCITERPARAMETERS.E1.value = component.E1
        rs_exciter.EXCITERPARAMETERS.Se1.value = component.Se1
        rs_exciter.EXCITERPARAMETERS.E2.value = component.E2
        rs_exciter.EXCITERPARAMETERS.Se2.value = component.Se2
        rs_exciter.EXCITERPARAMETERS.Vmn.value = component.Vrmin
        rs_exciter.EXCITERPARAMETERS.Vmx.value = component.Vrmax
        rs_exciter.CONFIGURATION.Gen.value = RSCADComponentBuilder.sanitize_string(
            generator.name
        )
        return rs_exciter
