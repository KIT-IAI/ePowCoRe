import pyapi_rts.generated.rtdsPSS1Adef as rscadPSS1A
from epowcore.gdf.power_system_stabilizers import IEEEPSS1A as PSS1A
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


class RSCADPSS1A(RSCADComponentBuilder):
    @classmethod
    def get_connection_point(
        cls, component: rscadPSS1A.rtdsPSS1Adef, connection: str
    ) -> tuple[int, int]:
        points = component.connection_points.get(connection)
        if points is None:
            raise ValueError(f"Connection point {connection} not found")
        return points.position_abs

    @classmethod
    def create(  # type: ignore[override]
        cls, component: PSS1A, base_frequency: float, generator: SynchronousMachine
    ) -> rscadPSS1A.rtdsPSS1Adef:
        """Creates a RSCAD IEEEG1 governor from a core model IEEEG1 governor element and sets the available values and sets the generator name"""
        rs_pss = rscadPSS1A.rtdsPSS1Adef()
        rs_pss.CONFIGURATION.HTZ.value = base_frequency
        # TODO: Options which generator signal is used. This changes the connection points of the component.
        # if pss.Vsi_in == 0:
        #     rscadPss.PSSPARAMETERS.j.value = JEnumParameter.JEnum.w)
        # if pss.Vsi_in == 1:
        #     rscadPss.PSSPARAMETERS.j.value = JEnumParameter.JEnum.F)
        # if pss.Vsi_in == 3:
        #     rscadPss.PSSPARAMETERS.j.value = JEnumParameter.JEnum.Pe)
        rs_pss.PSSPARAMETERS.A1.value = component.A1
        rs_pss.PSSPARAMETERS.A2.value = component.A2
        rs_pss.PSSPARAMETERS.T1.value = component.T1
        rs_pss.PSSPARAMETERS.T2.value = component.T2
        rs_pss.PSSPARAMETERS.T3.value = component.T3
        rs_pss.PSSPARAMETERS.T4.value = component.T4
        rs_pss.PSSPARAMETERS.T5.value = component.T5
        rs_pss.PSSPARAMETERS.T6.value = component.T6
        rs_pss.PSSPARAMETERS.KS.value = component.Ks
        rs_pss.PSSPARAMETERS.Vrmax.value = component.Vst_max
        rs_pss.PSSPARAMETERS.Vrmin.value = component.Vst_min

        # Activate enumeration
        rs_pss.enumeration.is_active = True
        rs_pss.SIGNALNAMES.VMPU.value = "Vpu#"
        rs_pss.CONFIGURATION.Gen.value = RSCADComponentBuilder.sanitize_string(
            generator.name
        )
        rs_pss.enumeration.enumeration_string = rs_pss.name
        return rs_pss
