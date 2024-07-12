import pyapi_rts.generated.rtdsEXST1Adef as rscadIEEEST1A
from epowcore.gdf.exciters.ieee_st1a import IEEEST1A
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine

from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


class RSCADIEEEST1A(RSCADComponentBuilder):
    @classmethod
    def get_connection_point(
        cls, component: rscadIEEEST1A.rtdsEXST1Adef, connection: str
    ) -> tuple[int, int]:
        points = component.connection_points.get(connection)
        if points is None:
            raise ValueError(f"Connection point {connection} not found")
        return points.position_abs

    @classmethod
    def create(  # type: ignore[override]
        cls, component: IEEEST1A, base_frequency: float, generator: SynchronousMachine
    ) -> rscadIEEEST1A.rtdsEXST1Adef:
        """
        Creates a RSCAD ieeeest1a exciter from a core model ieeeest1a exciter element and sets the available values, including the generator name from a core model generator element
        """
        rs_exciter = rscadIEEEST1A.rtdsEXST1Adef()
        rs_exciter.CONFIGURATION.HTZ.value = base_frequency
        rs_exciter.EXCITERPARAMETERS.Vimx.value = component.Vi_max
        rs_exciter.EXCITERPARAMETERS.Vimn.value = component.Vi_min
        rs_exciter.EXCITERPARAMETERS.Tc.value = component.Tc
        rs_exciter.EXCITERPARAMETERS.Tb.value = component.Tb
        rs_exciter.EXCITERPARAMETERS.Tc1.value = component.Tc1
        rs_exciter.EXCITERPARAMETERS.Tb1.value = component.Tb1
        rs_exciter.EXCITERPARAMETERS.Ka.value = component.Ka
        rs_exciter.EXCITERPARAMETERS.Ta.value = component.Ta
        rs_exciter.EXCITERPARAMETERS.Vamx.value = component.Va_max
        rs_exciter.EXCITERPARAMETERS.Vamn.value = component.Va_min
        rs_exciter.EXCITERPARAMETERS.Vrmx.value = component.Vr_max
        rs_exciter.EXCITERPARAMETERS.Vrmn.value = component.Vr_min
        rs_exciter.EXCITERPARAMETERS.Kc.value = component.Kc
        rs_exciter.EXCITERPARAMETERS.Kf.value = component.Kf
        rs_exciter.EXCITERPARAMETERS.Tf.value = component.Tf
        rs_exciter.EXCITERPARAMETERS.Klr.value = component.Klr
        rs_exciter.EXCITERPARAMETERS.Ilr.value = component.Ilr
        rs_exciter.CONFIGURATION.Gen.value = RSCADComponentBuilder.sanitize_string(
            generator.name
        )
        return rs_exciter
