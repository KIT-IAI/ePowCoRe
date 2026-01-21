from epowcore.gdf.bus import LFBusType
from epowcore.gdf.generators.epow_generator import EPowGenerator
from epowcore.gdf.generators.generator import Generator
from epowcore.gdf.exciters import Exciter
from epowcore.gdf.governors import Governor
from epowcore.gdf.power_system_stabilizers import PowerSystemStabilizer
from epowcore.gdf.generators.static_generator import StaticGenerator
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.utils import get_connected_bus
from epowcore.generic.logger import Logger
from epowcore.power_factory.utils import get_pf_grid_component, add_cubicle_to_bus
from epowcore.power_factory.from_gdf.components.exciter import create_exciter
from epowcore.power_factory.from_gdf.components.governor import create_governor
from epowcore.power_factory.from_gdf.components.power_system_stabilizer import create_pss



def create_synchronous_machine(self, gen: SynchronousMachine) -> bool:
    """Convert and add the given gdf core model synchronous machine to the given
    powerfactory network.

    :param gen: GDF core_model synchronous machine to be converted.
    :type gen: SynchronousMachine
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    success = True

    # Create generator inside of network
    pf_gen = self.pf_grid.CreateObject("ElmSym", gen.name)

    # Get bus connected to the generator
    gdf_gen_bus = get_connected_bus(graph=self.core_model.graph, node=gen, max_depth=1)

    if gdf_gen_bus is None:
        Logger.log_to_selected(
            f"There was no generator bus found inside of the core_model network for the synchronous_machine {gen.name}"
        )
        success = False
    else:
        match gdf_gen_bus.lf_bus_type:
            case LFBusType.SL:
                pf_gen.SetAttribute("ip_ctrl", 1)
                pf_gen.SetAttribute("e:bustp", "SL")
            case LFBusType.PQ:
                pf_gen.SetAttribute("ip_ctrl", 0)
                pf_gen.SetAttribute("e:bustp", "PQ")
            case LFBusType.PV:
                pf_gen.SetAttribute("ip_ctrl", 0)
                pf_gen.SetAttribute("e:bustp", "PV")

    pf_gen_bus = get_pf_grid_component(self, component_name=gdf_gen_bus.name)
    if pf_gen_bus is None:
        Logger.log_to_selected(
            f"There was no generator bus found inside of the powerfactory network for the synchronous_machine {gen.name}"
        )
        success = False

    # If the bus was found set connection attribute
    if success:
        pf_gen.SetAttribute("bus1", add_cubicle_to_bus(pf_gen_bus))

    # Get generator types folder
    pf_gen_type_lib = self.pf_type_library.SearchObject(
        self.pf_type_library.GetFullName() + "\\Generator Types"
    )
    # Create new gen type
    pf_gen_type = pf_gen_type_lib.CreateObject("TypSym", gen.name + "_type")

    # Create generator power plant
    pf_power_plant = self.pf_grid.CreateObject("ElmComp", gen.name + " Power Plant")

    exciters = list(filter(lambda x: True if isinstance(x, Exciter) else False, self.core_model.get_neighbors(component=gen) ))
    governors = list(filter(lambda x: True if isinstance(x, Governor) else False, self.core_model.get_neighbors(component=gen) ))
    power_system_stabilizers = list(filter(lambda x: True if isinstance(x, PowerSystemStabilizer) else False, self.core_model.get_neighbors(component=gen) ))

    #lib = self.app.GetGlobalLibrary("BlkDef")
    pf_standard_power_plant_type = self.pf_digsilent_library.SearchObject("Arch\\PF 2022 Models\\DynPsse\\Frm\\SYM Frame_no droop.BlkDef")
    pf_power_plant.SetAttribute("typ_id", pf_standard_power_plant_type)


    pf_power_plant_pelm = []
    pf_power_plant_pblk = []
    
    pf_power_plant_pblk.append(self.pf_digsilent_library.GetContents("Sym Slot.BlkSlot", 1)[0])
    pf_power_plant_pelm.append(pf_gen)

    for exciter in exciters:
        pf_power_plant_pblk.append(self.pf_digsilent_library.GetContents("Avr Slot.BlkSlot", 1)[0])
        pf_power_plant_pelm.append(create_exciter(self, exciter, pf_power_plant))

    for governor in governors:
        pf_power_plant_pblk.append(self.pf_digsilent_library.GetContents("Gov Slot.BlkSlot", 1)[0])
        pf_power_plant_pelm.append(create_governor(self, governor, pf_power_plant))

    for pss in power_system_stabilizers:
        pf_power_plant_pblk.append(self.pf_digsilent_library.GetContents("Pss Slot.BlkSlot", 1)[0])
        pf_power_plant_pelm.append(create_pss(self, pss, pf_power_plant))

    pf_power_plant.SetAttribute("pblk", pf_power_plant_pblk)
    pf_power_plant.SetAttribute("pelm", pf_power_plant_pelm)

    # Set attributes for newly crated gen type
    pf_gen_type.SetAttribute("sgn", gen.rated_apparent_power)
    pf_gen_type.SetAttribute("ugn", gen.rated_voltage)
    pf_gen_type.SetAttribute("h", gen.inertia_constant)
    pf_gen_type.SetAttribute("r0sy", gen.zero_sequence_resistance)
    pf_gen_type.SetAttribute("x0sy", gen.zero_sequence_reactance)
    pf_gen_type.SetAttribute("xl", gen.stator_leakage_reactance)
    pf_gen_type.SetAttribute("rstr", gen.stator_resistance)
    pf_gen_type.SetAttribute("xd", gen.synchronous_reactance_x)
    pf_gen_type.SetAttribute("xds", gen.transient_reactance_x)
    pf_gen_type.SetAttribute("xdss", gen.subtransient_reactance_x)
    pf_gen_type.SetAttribute("xq", gen.synchronous_reactance_q)
    pf_gen_type.SetAttribute("xqs", gen.transient_reactance_q)
    pf_gen_type.SetAttribute("xqss", gen.subtransient_reactance_q)
    pf_gen_type.SetAttribute("tds0", gen.tds0)
    pf_gen_type.SetAttribute("tqs0", gen.tqs0)
    pf_gen_type.SetAttribute("tdss0", gen.tdss0)
    pf_gen_type.SetAttribute("tqss0", gen.tqss0)
    pf_gen_type.SetAttribute("Q_min", gen.q_min)
    pf_gen_type.SetAttribute("Q_max", gen.q_max)

    # Set attributes of the generator itself
    pf_gen.SetAttribute("pgini", gen.rated_active_power)
    # pf_gen.SetAttribute("m:P:bus1", gen.active_power)   # Attributes only known based on powerflow
    # pf_gen.SetAttribute("m:Q:bus1", gen.reactive_power)
    pf_gen.SetAttribute("usetp", gen.voltage_set_point)
    pf_gen.SetAttribute("Pmin_uc", gen.p_min)
    pf_gen.SetAttribute("P_max", gen.p_max)
    pf_gen.SetAttribute("Pmin_uc", gen.pc1)
    pf_gen.SetAttribute("Pmax_uc", gen.pc2)
    pf_gen.SetAttribute("cQ_min", gen.qc1_min)
    pf_gen.SetAttribute("cQ_max", gen.qc1_max)
    pf_gen.SetAttribute("cQ_min", gen.qc2_min)
    pf_gen.SetAttribute("cQ_max", gen.qc2_max)
    pf_gen.GPSlon = gen.coords[0]
    pf_gen.GPSlat = gen.coords[1]

    # Set gen type attribute to the newly crated gen type
    pf_gen.SetAttribute("typ_id", pf_gen_type)

    return success

def create_static_generator(self, gen: StaticGenerator) -> bool:
    """Convert and add the given gdf core model static generator to the given powerfactory network.

    :param gen: GDF core_model load to be converted.
    :type gen: StaticGenerator
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    success = True

    # Create generator inside of network
    pf_gen = self.pf_grid.CreateObject("ElmGenstat", gen.name)

    # Get bus connected to the generator
    gdf_gen_bus = get_connected_bus(graph=self.core_model.graph, node=gen, max_depth=1)

    if gdf_gen_bus is None:
        Logger.log_to_selected(
            f"There was no generator bus found inside of the core_model network for the static generator {gen.name}"
        )
        success = False
    else:
        if gdf_gen_bus.lf_bus_type == "SLACK":
            pf_gen.SetAttribute("ip_ctrl", 1)

    pf_gen_bus = get_pf_grid_component(self, component_name=gdf_gen_bus.name)
    if pf_gen_bus is None:
        Logger.log_to_selected(
            f"There was no generator bus found inside of the powerfactory network for the static generator {gen.name}"
        )
        success = False

    # If the bus was found set connection attribute
    if success:
        pf_gen.SetAttribute("bus1", add_cubicle_to_bus(pf_gen_bus))

    # Set attributes of the generator itself
    pf_gen.SetAttribute("sgn", gen.rated_apparent_power)
    pf_gen.SetAttribute("loc_name", gen.name)
    pf_gen.SetAttribute("pgini", gen.rated_active_power)
    pf_gen.SetAttribute("qgini", gen.reactive_power)
    pf_gen.SetAttribute("usetp", gen.voltage_set_point)
    pf_gen.SetAttribute("Pmin_uc", gen.p_min)
    pf_gen.SetAttribute("P_max", gen.p_max)
    pf_gen.SetAttribute("cQ_min", gen.q_min)
    pf_gen.SetAttribute("cQ_max", gen.q_max)
    pf_gen.GPSlon = gen.coords[0]
    pf_gen.GPSlat = gen.coords[1]

    return success
