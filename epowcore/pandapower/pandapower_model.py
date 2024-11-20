'''numpy providing the NaN (not a number) value'''
from numpy import nan

import pandapower

from dataclasses import dataclass, field
from epowcore.gdf.bus import Bus
from epowcore.gdf.switch import Switch
from epowcore.gdf.bus import BusType
from epowcore.gdf.load import Load
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine


from epowcore.generic.logger import Logger
from epowcore.gdf.utils import get_connected_bus

@dataclass(kw_only=True)
class PandapowerModel:
    '''Wrapper class around a Pandapower Network, 
    with functionality for the conversion from gdf to pandapower'''
    network: pandapower.pandapowerNet

    def create_bus_from_gdf(self, bus: Bus):
        '''Create a pandapower bus in the PandapowerModel Network from a given gdf bus'''
        pandapower_type = "b"
        if Bus.bus_type == BusType.JUNCTION:
            pandapower_type = "n"

        pandapower.create_bus(
            net = self.network,
            vn_kv = bus.nominal_voltage,
            name = bus.name,
            index = bus.uid,
            type = pandapower_type,
            zone=None,
            in_service=True,
            max_vm_pu=nan,
            min_vm_pu=nan,
            geodata = bus.coords,
        )

    def create_load_from_gdf(self, core_model: CoreModel, load: Load) -> bool:
        '''Create a pandapower load in the PandapowerModel Network from a load in the CoreModel
        Currently using the get_connected_bus method to find the bus the load is connected to, 
        because a connection bus is needed for Pandapower to creat a load'''
        # Searching load bus
        load_bus = get_connected_bus(core_model.graph, load, max_depth=1)

        if load_bus is None:
            Logger.log_to_selected("Their was no bus found connected to the load")
            return False
        pandapower.create_load(
            net = self.network,
            bus = load_bus.uid,
            p_mw = load.active_power,
            q_mvar = load.reactive_power,
            const_z_percent=0,
            const_i_percent=0,
            sn_mva=nan,
            name = load.name,
            scaling=1.0,
            index=None,
            in_service=True,
            type='wye',
            max_p_mw=nan,
            min_p_mw=nan,
            max_q_mvar=nan,
            min_q_mvar=nan,
            controllable=nan,
        )
        return True

    def create_two_winding_transformer_from_gdf(self, core_model: CoreModel, transformer: TwoWindingTransformer):
        '''Create two winding pandapower transformer based on a given two winding transformer from gdf
        and add it into the network'''

        high_voltage_bus = core_model.get_neighbors(
            component = transformer,
            follow_links=True,
            connector = 'HV'
        )[0]
        low_voltage_bus = core_model.get_neighbors(
            component = transformer,
            follow_links=True,
            connector = 'LV'
        )[0]

        if high_voltage_bus is None or low_voltage_bus is None:
            Logger.log_to_selected("Failled to convert transformer")
            return False

        pandapower.create_transformer_from_parameters(
            net = self.network,
            index = transformer.uid,
            hv_bus = high_voltage_bus.uid,
            lv_bus = low_voltage_bus.uid,
            sn_mva = transformer.rating,
            vn_hv_kv = transformer.voltage_hv,
            vn_lv_kv = transformer.voltage_lv,
            vkr_percent = 0,  # ToDo, setting a default because the value is unclear.
            vk_percent = 0,  # ToDo, setting a default because the value is unclear.
            pfe_kw = transformer.pfe_kw,
            i0_percent = 0,  # ToDo, setting a default because the value is unklear. (maybe pfe_pu)
            shift_degree = transformer.phase_shift_30 * 30,  # Calculating phase shift
            tap_side = "hv",  # Not represented in GDF, setting it by default to high side
            tap_neutral = transformer.tap_neutral,
            tap_max = transformer.tap_max,
            tap_min = transformer.tap_min,
            # tap step per percent or per unit are equivalent because 
            # both are relative measures to the nominal voltage of the high voltage side
            tap_step_percent = transformer.tap_changer_voltage,
            tap_step_degree=nan,
            tap_pos = transformer.tap_initial,
            tap_phase_shifter=False,
            in_service=True,
            name = transformer.name,
            vector_group=None,
            max_loading_percent=nan,
            parallel=1,
            df=1.0,
            vk0_percent=nan,
            vkr0_percent=nan,
            # Not sure previously set to transformer.zm_pu, 
            # but this was dependet of no load current which is also not given
            mag0_percent = nan,  
            mag0_rx = transformer.rm_pu,  # Not sure
            si0_hv_partial=nan,
            pt_percent=nan,
            oltc=nan,
            tap_dependent_impedance=nan,
            vk_percent_characteristic=None,
            vkr_percent_characteristic=None,
            xn_ohm=nan,
            tap2_side=None,
            tap2_neutral=nan,
            tap2_max=nan,
            tap2_min=nan,
            tap2_step_percent=nan,
            tap2_step_degree=nan,
            tap2_pos=nan,
            tap2_phase_shifter=nan,
        )
        return True
    
    def create_generator_from_gdf_sychronous_maschine(self, core_model: CoreModel, synchronous_maschine: SynchronousMachine):
        '''Create a generator in the pandapower network equivalent to the given synchronous_maschine in gdf format'''

        generator_bus = get_connected_bus(core_model.graph, synchronous_maschine, max_depth=1)

        if generator_bus is None:
            Logger.log_to_selected("Failed to convert synchonous_maschine")
            return False

        pandapower.create.create_gen(
            net = self.network,
            bus = generator_bus.uid,
            p_mw = synchronous_maschine.active_power,
            vm_pu = synchronous_maschine.voltage_set_point,
            sn_mva = synchronous_maschine.rated_apparent_power,  # not completly sure
            name = synchronous_maschine.name,
            index = synchronous_maschine.uid,
            max_q_mvar = synchronous_maschine.q_max,
            min_q_mvar = synchronous_maschine.q_min,
            min_p_mw = synchronous_maschine.p_min,
            max_p_mw = synchronous_maschine.p_max,
            min_vm_pu=nan,
            max_vm_pu=nan,  # maybe rated_voltage
            scaling=1.0,
            type = "sync",
            slack = True,  # So the generator will be incoporated correctly?
            controllable = True,
            vn_kv = synchronous_maschine.rated_voltage,
            # Unsure if not subtransient_reactance_q ???(same description)
            xdss_pu = synchronous_maschine.subtransient_reactance_x,
            rdss_ohm=nan,
            cos_phi=nan,
            pg_percent=nan,
            power_station_trafo=nan,
            in_service=True,
            slack_weight=0.0,
        )
        return True
