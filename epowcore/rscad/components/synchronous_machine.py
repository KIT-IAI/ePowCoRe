import logging

import pyapi_rts.generated.lfrtdssharcsldMACV31 as rscadSynchronousMachineMACV31
from pyapi_rts.generated.enums.Noyes2EnumParameter import Noyes2Enum

from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


class RSCADSynchronousMachine(RSCADComponentBuilder):
    @classmethod
    def get_connection_point(
        cls,
        component: rscadSynchronousMachineMACV31.lfrtdssharcsldMACV31,
        connection: str,
    ) -> tuple[int, int]:
        # TODO: Also include wire labels?
        a1 = component.connection_points.get("A_1")
        if a1 is None:
            raise ValueError(f"Connection point A_1 not found in {component.name} {component.type}")
        return a1.position_abs

    @classmethod
    def create(  # type: ignore[override]
        cls, component: SynchronousMachine, base_frequency: float = 60.0
    ) -> rscadSynchronousMachineMACV31.lfrtdssharcsldMACV31:
        """Creates a RSCAD synchronous machine from a datastructure 3-winding transformer element and sets the available values"""
        sync_machine = rscadSynchronousMachineMACV31.lfrtdssharcsldMACV31()
        sync_machine.GENERALMODELCONFIGURATION.Name.value = RSCADComponentBuilder.sanitize_string(
            component.name
        )
        sync_machine.MACHINEINITIALLOADFLOWDATA.P0.value = component.rated_active_power
        sync_machine.MACHINEINITIALLOADFLOWDATA.Q0.value = component.reactive_power
        sync_machine.GENERALMODELCONFIGURATION.mmva.value = component.rated_apparent_power
        sync_machine.GENERALMODELCONFIGURATION.Vbsll.value = component.rated_voltage
        sync_machine.GENERALMODELCONFIGURATION.HTZ.value = base_frequency
        sync_machine.GENERALMODELCONFIGURATION.trfmr.value = Noyes2Enum.No
        # Check minimum
        if component.zero_sequence_resistance < 0.000125:
            sync_machine.MACHINEZEROSEQUENCEIMPEDANCES.Mrzro.value = 0.00125
            logging.info("%s|%s| Mrzro:%e", sync_machine.type, sync_machine.name, 0.000125)
        else:
            sync_machine.MACHINEZEROSEQUENCEIMPEDANCES.Mrzro.value = (
                component.zero_sequence_resistance
            )
        sync_machine.MACHINEZEROSEQUENCEIMPEDANCES.Mxzro.value = component.zero_sequence_reactance
        sync_machine.MACHINEELECTDATAGENERATORFORMAT.Xa.value = component.stator_leakage_reactance
        sync_machine.MACHINEELECTDATAGENERATORFORMAT.Xq.value = component.synchronous_reactance_q
        if component.synchronous_reactance_q <= component.transient_reactance_q:
            sync_machine.MACHINEELECTDATAGENERATORFORMAT.Xqtr.value = (
                component.synchronous_reactance_q - 0.01
            )
        else:
            sync_machine.MACHINEELECTDATAGENERATORFORMAT.Xqtr.value = (
                component.transient_reactance_q
            )
        sync_machine.MACHINEELECTDATAGENERATORFORMAT.Xqsubtr.value = (
            component.subtransient_reactance_q
        )
        sync_machine.MACHINEELECTDATAGENERATORFORMAT.Xd.value = component.synchronous_reactance_x
        sync_machine.MACHINEELECTDATAGENERATORFORMAT.Xdtr.value = component.transient_reactance_x
        sync_machine.MACHINEELECTDATAGENERATORFORMAT.Xdsubtr.value = (
            component.subtransient_reactance_x
        )

        # Disable optional transformer
        sync_machine.GENERALMODELCONFIGURATION.trfmr.value = Noyes2Enum.No
        # Activate and set name enumeration
        sync_machine.enumeration.is_active = True
        sync_machine.enumeration.enumeration_string = sync_machine.name
        sync_machine.SIGNALMONITORINGINRTANDCCMAC.mon1.value = Noyes2Enum.Yes
        sync_machine.SIGNALMONITORINGINRTANDCCMAC.mon2.value = Noyes2Enum.Yes
        sync_machine.MECHANICALDATAANDCONFIGURATION.H.value = component.inertia_constant
        sync_machine.MACHINEINITIALLOADFLOWDATA.Pt.value = component.rated_active_power
        sync_machine.MACHINEINITIALLOADFLOWDATA.Qt.value = component.reactive_power
        sync_machine.MACHINEINITIALLOADFLOWDATA.Vmagn.value = component.voltage_set_point
        return sync_machine
