"""pandapower_model module providing the PandapowerModel class used to create
the converted pandapower network.
"""

from dataclasses import dataclass
import math
import numpy as np

import pandapower

from epowcore.gdf.bus import Bus, BusType, LFBusType
from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.load import Load
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.switch import Switch
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.utils import get_connected_bus
from epowcore.gdf.ward import Ward
from epowcore.generic.logger import Logger


@dataclass(kw_only=True)
class PandapowerModel:
    """Wrapper class around a Pandapower Network,
    with functions that take a gdf component of a kind and create a
    equivalent component in the pandapower network.
    """

    network: pandapower.pandapowerNet

    def create_bus_from_gdf(self, bus: Bus):
        """Create a pandapower bus in the pandapower network
        from a given gdf bus.

        :param bus: gdf bus to be converted and added
                    to the pandapower network.
        :type bus: Bus
        """
        pandapower_type = "b"
        if Bus.bus_type == BusType.JUNCTION:
            pandapower_type = "n"
        # Creating the bus in the Pandapower Network
        pandapower.create_bus(
            net=self.network,
            name=bus.name,
            index=bus.uid,
            geodata=bus.coords,
            coords=bus.coords,
            vn_kv=bus.nominal_voltage,
            type=pandapower_type,
            zone=None,
            in_service=True,
            max_vm_pu=np.nan,
            min_vm_pu=np.nan,
        )

    def create_load_from_gdf(self, core_model: CoreModel, load: Load) -> bool:
        """Create a pandapower load in the pandapower network from a
        load in the CoreModel. Returns True if there is a bus found connected to
        the load, returns False and doesn't create a load in the pandapower network
        if there is no connected bus found.

        :param core_model: Core model to be converted.
        :type core_model: CoreModel
        :param load: Load in the core model that will be converted and added
                     to the converted PandapowerModel.
        :type load: Load
        :return: Returns False if the conversion fails and True if it suceeds.
        :rtype: bool
        """
        # Getting load bus
        load_bus = get_connected_bus(core_model.graph, load, max_depth=1)
        # If no load bus was found the function fails
        if load_bus is None:
            Logger.log_to_selected("Their was no bus found connected to the load")
            return False
        # Create the pandapower load in the network
        pandapower.create_load(
            net=self.network,
            name=load.name,
            index=load.uid,
            bus=load_bus.uid,
            p_mw=load.active_power,
            q_mvar=load.reactive_power,
            const_z_percent=load.get_default(attr="const_z_percent"),
            const_i_percent=load.get_default(attr="const_i_percent"),
            sn_mva=np.nan,
            scaling=1.0,
            in_service=True,
            type=load.get_default(attr=type),
            max_p_mw=np.nan,
            min_p_mw=np.nan,
            max_q_mvar=np.nan,
            min_q_mvar=np.nan,
            controllable=np.nan,
        )
        return True

    def create_two_winding_transformer_from_gdf(
        self, core_model: CoreModel, transformer: TwoWindingTransformer
    ) -> bool:
        """Create a two winding pandapower transformer based on a given
        two winding transformer from gdf and add it into the network. Returns True
        if the high and low voltage bus are found, if not returns False and doesn't
        create a the two winding transformer in the pandapower network.

        :param core_model: Core model to be converted.
        :type core_model: CoreModel
        :param transformer: Two winding transformer in the core model that
                            will be converted and added to the converted 
                            pandapower model.
        :type transformer: TwoWindingTransformer
        :return: Return False if the conversion fails and True if it suceeds.
        :rtype: bool
        """
        # Get the bus connected to the transformer on the high voltage side
        high_voltage_bus = core_model.get_neighbors(
            component=transformer, follow_links=True, connector="HV"
        )[0]
        # Get the bus connected to the transformer on the low voltage side
        low_voltage_bus = core_model.get_neighbors(
            component=transformer, follow_links=True, connector="LV"
        )[0]
        # If either bus wasnt found the function failed
        if high_voltage_bus is None or low_voltage_bus is None:
            Logger.log_to_selected("Failled to convert two winding transformer")
            return False
        # Calculate parameters
        # uktrr in pandapower powerfactory converter
        vkr_percent = (
            math.sqrt(transformer.r1pu**2 + transformer.x1pu**2)
            * 100
            * transformer.r1pu
            / transformer.x1pu
        )
        # uktr in pandapower powerfactory converter
        vk_percent = math.sqrt(transformer.r1pu**2 + transformer.x1pu**2) * 100
        # pandapower powerfactory converter: uk0tr
        vk0_percent = vk_percent
        # ur0tr in pandapower powerfactory converter
        if transformer.r1pu == 0 or transformer.x1pu == 0:
            vkr0_percent = 0.0
        else:
            vkr0_percent = vk_percent / (transformer.r1pu / transformer.x1pu)
        # Create transformer in pandapower network
        pandapower.create_transformer_from_parameters(
            net=self.network,
            name=transformer.name,
            index=transformer.uid,
            hv_bus=high_voltage_bus.uid,
            lv_bus=low_voltage_bus.uid,
            sn_mva=transformer.rating,
            vn_hv_kv=transformer.voltage_hv,
            vn_lv_kv=transformer.voltage_lv,
            # Pandapower converter references the uktrr powerfactory variable, which isn't defined
            # any further in the technical reference and not featured in the gdf transformer
            vkr_percent=vkr_percent,
            vk_percent=vk_percent,
            pfe_kw=transformer.pfe_kw,
            i0_percent=transformer.no_load_current,
            shift_degree=transformer.phase_shift_30 * 30,
            tap_side="hv",
            tap_neutral=transformer.tap_neutral,
            tap_max=transformer.tap_max,
            tap_min=transformer.tap_min,
            tap_step_percent=transformer.tap_changer_voltage * 100,
            tap_step_degree=np.nan,
            tap_pos=transformer.tap_initial,
            tap_phase_shifter=False,
            # Assuming neutral position is the voltage the tap tries to hold
            in_service=True,
            vector_group=None,
            max_loading_percent=np.nan,
            parallel=1,
            df=1.0,
            vk0_percent=vk0_percent,
            vkr0_percent=vkr0_percent,
            # pandapower powerfactory converter: zx0hl_n
            # z0 needed for calculation
            mag0_percent=transformer.get_default(attr="mag0_percent"),
            # pandapower powerfactory converter: rtox0_n
            # z0 needed for calculation
            mag0_rx=transformer.get_default(attr="mag0_rx"),
            # pandapower powerfactory converter: zx0hl_n
            # z0 needed for calculation
            si0_hv_partial=transformer.get_default(attr="si0_hv_partial"),
            pt_percent=np.nan,
            oltc=np.nan,
            tap_dependent_impedance=np.nan,
            vk_percent_characteristic=None,
            vkr_percent_characteristic=None,
            xn_ohm=np.nan,
            tap2_side=None,
            tap2_neutral=np.nan,
            tap2_max=np.nan,
            tap2_min=np.nan,
            tap2_step_percent=np.nan,
            tap2_step_degree=np.nan,
            tap2_pos=np.nan,
            tap2_phase_shifter=np.nan,
        )
        return True

    def create_three_winding_transformer_from_gdf(
        self, core_model: CoreModel, transformer3w: ThreeWindingTransformer
    ) -> bool:
        """Create a thee winding pandapower transformer based on a given
        three winding transformer from gdf and add it into the network. Returns
        True if high, middle and low voltage bus are found, if not returns False
        and doesn't create a three winding transformer in the pandapower network.


        :param core_model: Core model to be converted.
        :type core_model: CoreModel
        :param transformer3w: Three winding transformer in the core model that
                              will be converted and added to the converted
                              pandapower model.
        :type transformer3w: ThreeWindingTransformer
        :return: Return False if the conversion fails and True if it suceeds.
        :rtype: bool
        """
        # Get the bus connected to the transformer on the high voltage side
        high_voltage_bus = core_model.get_neighbors(
            component=transformer3w, follow_links=True, connector="HV"
        )[0]
        # Get the bus connected to the transformer on the middle voltage side
        middle_voltage_bus = core_model.get_neighbors(
            component=transformer3w, follow_links=True, connector="MV"
        )
        # Get the bus connected to the transformer on the low voltage side
        low_voltage_bus = core_model.get_neighbors(
            component=transformer3w, follow_links=True, connector="LV"
        )[0]
        # If either bus wasnt found the function failed
        if high_voltage_bus is None or low_voltage_bus is None or middle_voltage_bus is None:
            Logger.log_to_selected("Failled to convert three winding transformer")
            return False
        # Create transformer in pandapower network
        pandapower.create.create_transformer3w_from_parameters(
            net=self.network,
            name=transformer3w.name,
            index=transformer3w.uid,
            hv_bus=high_voltage_bus.uid,
            mv_bus=middle_voltage_bus.uid,
            lv_bus=low_voltage_bus.uid,
            vn_hv_kv=transformer3w.voltage_hv,
            vn_mv_kv=transformer3w.voltage_mv,
            vn_lv_kv=transformer3w.voltage_lv,
            sn_hv_mva=transformer3w.rating_hv,
            sn_mv_mva=transformer3w.rating_mv,
            sn_lv_mva=transformer3w.rating_lv,
            vk_hv_percent=transformer3w.get_default(attr="vk_percent"),
            vk_mv_percent=transformer3w.get_default(attr="vk_percent"),
            vk_lv_percent=transformer3w.get_default(attr="vk_percent"),
            vkr_hv_percent=transformer3w.get_default(attr="vkr_hv_percent"),
            vkr_mv_percent=transformer3w.get_default(attr="vkr_hv_percent"),
            vkr_lv_percent=transformer3w.get_default(attr="vkr_hv_percent"),
            pfe_kw=transformer3w.pfe_kw,
            i0_percent=transformer3w.no_load_current,
            shift_mv_degree=transformer3w.phase_shift_30_mv * 30,
            shift_lv_degree=transformer3w.phase_shift_30_lv * 30,
            tap_side="hv",
            tap_step_percent=transformer3w.TapDetails.tap_changer_voltage * 100,
            tap_step_degree=np.nan,
            tap_pos=transformer3w.TapDetails.tap_initial,
            tap_neutral=transformer3w.TapDetails.tap_neutral,
            tap_max=transformer3w.TapDetails.tap_max,
            tap_min=transformer3w.TapDetails.tap_min,
            in_service=True,
            max_loading_percent=np.nan,
            tap_at_star_point=False,
            vk0_hv_percent=np.nan,
            vk0_mv_percent=np.nan,
            vk0_lv_percent=np.nan,
            vkr0_hv_percent=np.nan,
            vkr0_mv_percent=np.nan,
            vkr0_lv_percent=np.nan,
            vector_group=None,
            tap_dependent_impedance=np.nan,
            vk_hv_percent_characteristic=None,
            vkr_hv_percent_characteristic=None,
            vk_mv_percent_characteristic=None,
            vkr_mv_percent_characteristic=None,
            vk_lv_percent_characteristic=None,
            vkr_lv_percent_characteristic=None,
        )
        return True

    def create_generator_from_gdf_synchronous_machine(
        self, core_model: CoreModel, synchronous_machine: SynchronousMachine
    ) -> bool:
        """Create a generator in the pandapower network equivalent to
        the given synchronous machine in gdf format. Returns True if synchronous machine
        bus is found, if not returns False and doesn't create a generator in the
        pandapower network.

        :param core_model: Core model to be converted.
        :type core_model: CoreModel
        :param synchronous_machine: Synchronous machine in the core mode that will
                                    be converted and added to the converted
                                    pandapower model.
        :type synchronous_machine: SynchronousMachine
        :return: Return False if the conversion fails and True if it suceeds.
        :rtype: bool
        """
        # Getting the bus the generator is connected to
        synchronous_machine_bus = get_connected_bus(
            core_model.graph, synchronous_machine, max_depth=1
        )
        # If the bus wasnt found the function fails
        if synchronous_machine_bus is None:
            Logger.log_to_selected("Failed to convert synchonous_machine")
            return False

        # Check if the generator bus was slack
        slack = False
        if synchronous_machine_bus.lf_bus_type == LFBusType.SL:
            slack = True
            Logger.log_to_selected(
                "Gen:" + synchronous_machine.name + " is set to be a slack genenerator"
            )
        # Create generator in pandapower network
        pandapower.create_gen(
            net=self.network,
            name=synchronous_machine.name,
            index=synchronous_machine.uid,
            bus=synchronous_machine_bus.uid,
            # active_power or rated_active_power
            # -> makes no difference for IEEE39
            # leaving active_power because its by definition more fitting
            # (even though rated_active_power is used in pandapower converter)
            p_mw=synchronous_machine.rated_active_power,
            vm_pu=synchronous_machine.voltage_set_point,
            # or rated active power
            sn_mva=synchronous_machine.rated_apparent_power,
            max_q_mvar=synchronous_machine.q_max,
            min_q_mvar=synchronous_machine.q_min,
            min_p_mw=synchronous_machine.p_min,
            max_p_mw=synchronous_machine.p_max,
            min_vm_pu=np.nan,
            max_vm_pu=np.nan,
            scaling=1.0,
            type="sync",
            slack=slack,
            controllable=False,
            vn_kv=synchronous_machine.rated_voltage,
            xdss_pu=synchronous_machine.subtransient_reactance_x,
            rdss_ohm=np.nan,
            cos_phi=np.nan,
            pg_percent=np.nan,
            power_station_trafo=np.nan,
            in_service=True,
            slack_weight=0.0,
        )
        return True

    def create_line_from_gdf_tline(self, core_model: CoreModel, tline: TLine) -> bool:
        """Create a pandapower line in the network equivalent to a gdf
        transmission line. Returns True if a bus is found at both ends of the
        transmission line, if not returns False and doesn't create a line in
        the pandapower network.
        

        :param core_model: Core model to be converted.
        :type core_model: CoreModel
        :param tline: Transmission line in the gdf that will be converted and
                      added to the converted pandapower model.
        :type tline: TLine
        :return: Return False if the conversion fails and True if it suceeds.
        :rtype: bool
        """
        # Get the neigbours of the transmission line to know what it connects to
        from_bus = core_model.get_neighbors(component=tline, follow_links=True, connector="A")[0]
        to_bus = core_model.get_neighbors(component=tline, follow_links=True, connector="B")[0]
        # Conversion fails if one of the buses isn't found
        if from_bus is None or to_bus is None:
            print("Conversion of " + tline.name + " failed")
            return False
        network_frequency = core_model.base_frequency
        # Calculate rated current
        voltage = from_bus.nominal_voltage
        rated_current = tline.rating / voltage
        # Create line in pandapower network
        pandapower.create_line_from_parameters(
            net=self.network,
            name=tline.name,
            index=tline.uid,
            geodata=tline.coords,
            from_bus=from_bus.uid,
            to_bus=to_bus.uid,
            length_km=tline.length,
            r_ohm_per_km=tline.r1,
            x_ohm_per_km=tline.x1,
            c_nf_per_km=(tline.b1 * 1e3) / (2 * math.pi * network_frequency),
            max_i_ka=rated_current,
            type=None,
            in_service=True,
            df=1.0,
            parallel=tline.parallel_lines,
            g_us_per_km=0.0,
            max_loading_percent=np.nan,
            alpha=tline.get_default(attr="alpha"),
            temperature_degree_celsius=tline.get_default(attr="temperature_degree_celsius"),
            r0_ohm_per_km=tline.r0_fb(),
            x0_ohm_per_km=tline.x0_fb(),
            c0_nf_per_km=np.nan,
            g0_us_per_km=0,
            endtemp_degree=np.nan,
        )
        return True

    def create_ward_from_gdf_ward(self, core_model: CoreModel, ward: Ward) -> bool:
        """Create a ward in the pandapower network equivalent to a given
        ward from the gdf. Returns True if ward bus is found, if not returns False
        and doesn't create a ward in the pandapower network.

        :param core_model: Core model to be converted.
        :type core_model: CoreModel
        :param ward: Ward in the gdf that will be converted and added to the converted
                     pandapower network.
        :type ward: Ward
        :return: Return False if the conversion fails and True if it suceeds.
        :rtype: bool
        """

        ward_bus = get_connected_bus(core_model.graph, ward, max_depth=1)
        # If there was no ward_bus found the function failed and terminates
        if ward_bus is None:
            return False
        # Create ward in pandapower network
        pandapower.create_ward(
            net=self.network,
            name=ward.name,
            index=ward.uid,
            bus=ward_bus,
            ps_mw=-ward.p_gen + ward.p_load,
            qs_mvar=-ward.q_gen + ward.q_load,
            pz_mw=ward.p_zload,
            qz_mvar=ward.q_zload,
            in_service=True,
        )
        return True

    def create_shunt_from_gdf_shunt(self, core_model: CoreModel, shunt: Shunt) -> bool:
        """Create a shunt in the pandapower network equivalent to a given
        shunt from gdf. Returns True if a shunt bus is found, if not returns False
        and doesn't create a shunt in the pandapower network.

        :param core_model: Core model to be converted.
        :type core_model: CoreModel
        :param shunt: Shunt in the gdf that will be converted and added to the 
                      converted pandapower network.
        :type shunt: Shunt
        :return: Return False if the conversion fails and True if it suceeds.
        :rtype: bool
        """

        shunt_bus = get_connected_bus(core_model.graph, shunt, max_depth=1)
        # If there was no shunt_bus found the function failed and terminates
        if shunt_bus is None:
            return False
        # Create shunt in pandapower network
        pandapower.create_shunt(
            net=self.network,
            index=shunt.uid,
            bus=shunt_bus,
            p_mw=shunt.p,
            q_mvar=shunt.q,
        )
        return True

    def _create_pandapower_switch_et(self, component: Component) -> str | bool:
        """Return the right value for the et variable of the pandapower switch
        based on the given gdf component.
        False if the component is not of the type Bus, transmission Line,
        two winding transformer or three winding transform. If its one of
        the named components a certain string is returned.

        :param component: Component to get the et variable for.
        :type component: Component
        :return: False or a certain string based on the type of the componen.
        :rtype: str | bool
        """

        match component:
            case Bus():
                return "b"
            case TLine():
                return "I"
            case TwoWindingTransformer():
                return "t"
            case ThreeWindingTransformer():
                return "t3"
            case _:
                return False

    def create_switch_from_gdf_switch(self, core_model: CoreModel, switch: Switch) -> bool:
        """Create a pandapower switch in the network from a given gdf switch.
        Returns True if both neighbors are found and if the the switch et variable
        can be found, if not returns False and doesn't create a switch in the pandapower 
        network.

        :param core_model: Core model to be converted.
        :type core_model: CoreModel
        :param switch: Switch in the gdf that will be converted and added to the 
                       pandapower network.
        :type switch: Switch
        :return: Return False if the conversion fails and True if it suceeds.
        :rtype: bool
        """
        neighbours = core_model.get_neighbors(component=switch, follow_links=True, connector=None)
        # If there are less than two neighbours found the function fails
        if len(neighbours) == 2:
            if isinstance(neighbours[0], Bus):
                switch_bus = neighbours[0].uid
                switch_other_component = neighbours[1].uid
            else:
                switch_bus = neighbours[1].uid
                switch_other_component = neighbours[0].uid
        else:
            return False
        # Get string mapped to the type of the other component
        switch_et = self._create_pandapower_switch_et(switch_other_component)
        # If it wasn't possible to map the component the function fails
        if not switch_et:
            Logger.log_to_selected(
                "Failed to convert " + switch.name + " because of the connected components"
            )
            return False
        voltage = switch_bus.nominal_voltage
        # Create swith in the pandapower network
        pandapower.create_switch(
            net=self.network,
            name=switch.name,
            index=switch.uid,
            bus=switch_bus,
            element=switch_other_component,
            et=switch_et,
            closed=switch.closed,
            in_ka=switch.rating_b * 1000 / voltage,
        )
        return True
