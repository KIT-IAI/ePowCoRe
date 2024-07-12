import pyapi_rts.generated.rtdsPTIST1def as rscadPTIST1
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.power_system_stabilizers.ptist1 import PTIST1
from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


class RSCADPTIST1(RSCADComponentBuilder):
    @classmethod
    def get_connection_point(
        cls, component: rscadPTIST1.rtdsPTIST1def, connection: str
    ) -> tuple[int, int]:
        point = component.connection_points.get(connection)
        if point is None:
            raise ValueError(f"Connection {connection} not found in {component.name}")
        return point.position_abs

    @classmethod
    def create(  # type: ignore[override]
        cls, component: PTIST1, base_frequency: float, generator: SynchronousMachine
    ) -> rscadPTIST1.rtdsPTIST1def:
        """Creates a RSCAD PTIST1 PSS from a datastructure PTIST1 PSS element and sets the available values and sets the generator name"""
        rs_pss = rscadPTIST1.rtdsPTIST1def()
        rs_pss.CONFIGURATION.HTZ.value = base_frequency
        rs_pss.PSSPARAMETERS.K.value = component.Kpss
        rs_pss.PSSPARAMETERS.Tf.value = component.Tw
        rs_pss.PSSPARAMETERS.T1.value = component.T1
        rs_pss.PSSPARAMETERS.T2.value = component.T2
        rs_pss.PSSPARAMETERS.T3.value = component.T3
        rs_pss.PSSPARAMETERS.T4.value = component.T4
        # Activate enumeration
        rs_pss.enumeration.is_active = True
        rs_pss.enumeration.enumeration_string = rs_pss.name
        rs_pss.CONFIGURATION.Gen.value = RSCADComponentBuilder.sanitize_string(
            generator.name
        )
        return rs_pss
