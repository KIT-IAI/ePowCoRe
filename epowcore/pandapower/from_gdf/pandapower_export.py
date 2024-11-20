from copy import deepcopy

from epowcore.gdf.bus import Bus
from epowcore.gdf.load import Load
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.logger import Logger
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer

from epowcore.pandapower.pandapower_model import PandapowerModel

from epowcore.generic.manipulation import flatten
import pandapower

def export_pandapower(core_model: CoreModel) -> PandapowerModel:

    # Create PandapowerModel that stores pandapower.Net to create elements inside of
    Logger.log_to_selected("Creating Pandapower network")
    pandapower_network= PandapowerModel(
        network = pandapower.create_empty_network(
            f_hz=core_model.base_frequency, sn_mva=core_model.base_mva_fb(), add_stdtypes=False
        )
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
        if pandapower_network.create_two_winding_transformer_from_gdf(core_model=core_model, transformer=gdf_two_winding_transformer):
            counter += 1
    Logger.log_to_selected(f"created {counter} out of {number_of_two_winding_transformers}")


    return pandapower_network
