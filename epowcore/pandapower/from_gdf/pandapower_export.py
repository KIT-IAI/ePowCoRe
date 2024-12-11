import pandapower

from epowcore.gdf.bus import Bus
from epowcore.gdf.tline import TLine
from epowcore.gdf.load import Load
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.logger import Logger
from epowcore.generic.constants import Platform
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.pandapower.pandapower_model import PandapowerModel



def export_pandapower(core_model: CoreModel) -> PandapowerModel:
    '''Pandapower export function, taking in the gdf CoreModel and returning
    a PandapowerModel object.
    '''

    # Create PandapowerModel that stores pandapower.Net to create elements inside of
    Logger.log_to_selected("Creating Pandapower network")
    pandapower_network= PandapowerModel(
        network = pandapower.create_empty_network(
            f_hz=core_model.base_frequency, sn_mva=core_model.base_mva_fb(), add_stdtypes=False
        ),
        platform=Platform("Pandapower")
    )

    Logger.log_to_selected("Creating buses in the Pandapower network")
    counter=0
    gdf_bus_list = core_model.type_list(Bus)
    number_of_buses = len(gdf_bus_list)
    for gdf_bus in gdf_bus_list:
        pandapower_network.create_bus_from_gdf(bus=gdf_bus)
        counter+=1
    Logger.log_to_selected(f"created {counter} out of {number_of_buses}")

    Logger.log_to_selected("Creating loads in the Pandapower network")
    counter=0
    gdf_load_list = core_model.type_list(Load)
    number_of_loads = len(gdf_load_list)
    for gdf_load in gdf_load_list:
        if pandapower_network.create_load_from_gdf(core_model=core_model, load=gdf_load):
            counter += 1
    Logger.log_to_selected(f"created {counter} out of {number_of_loads}")


    Logger.log_to_selected("Creating transformer in the Pandapower network")
    counter=0
    gdf_two_winding_transformer_list = core_model.type_list(TwoWindingTransformer)
    number_of_two_winding_transformers = len(gdf_two_winding_transformer_list)
    for gdf_two_winding_transformer in gdf_two_winding_transformer_list:
        if pandapower_network.create_two_winding_transformer_from_gdf(
            core_model=core_model,
            transformer=gdf_two_winding_transformer
        ):
            counter += 1
    Logger.log_to_selected(f"created {counter} out of {number_of_two_winding_transformers}")


    Logger.log_to_selected("Creating static generators from synchronous machines in the Pandapower network")
    counter = 0
    gdf_synchronous_machine_list = core_model.type_list(SynchronousMachine)
    number_of_synchronous_machines = len(gdf_synchronous_machine_list)
    for gdf_synchronous_machine in gdf_synchronous_machine_list:
        if pandapower_network.create_generator_from_gdf_synchronous_maschine(
            core_model=core_model,
            synchronous_maschine=gdf_synchronous_machine
        ):
            counter +=1
    Logger.log_to_selected(f"created {counter} out of {number_of_synchronous_machines}")

    Logger.log_to_selected("Creating lines from transmission lines in the pandapower network")
    counter = 0
    gdf_tline_list = core_model.type_list(TLine)
    number_of_tlines = len(gdf_tline_list)
    for gdf_tline in gdf_tline_list:
        if pandapower_network.create_line_from_gdf_tline(
            core_model=core_model,
            tline=gdf_tline
        ):
            counter +=1
    Logger.log_to_selected(f"Created {counter} out of {number_of_tlines}")

    return pandapower_network
