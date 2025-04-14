from epowcore.gdf.load import Load
from epowcore.generic.logger import Logger
from epowcore.gdf.utils import get_connected_bus
from epowcore.power_factory.utils import get_pf_grid_component


def create_load(self, load: Load) -> bool:
    """Convert and add the given gdf core model load to the given powerfactory network.

    :param load: GDF core_model load to be converted.
    :type load: Load
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    success = True

    # Create load inside of network
    pf_load = self.pf_grid.CreateObject("ElmLod")

    # Get connected bus
    # Maybe change this so the load gets converted without a connected bus if it is not found?
    gdf_load_bus = get_connected_bus(graph=self.core_model.graph, node=load, max_depth=1)
    # Check if connected bus exists
    if gdf_load_bus is None:
        Logger.log_to_selected(
            f"There was no load bus found inside of the core_model network for the load {load.name}"
        )
        success = False
    else:
        # Find the power factory bus with the same name
        pf_load_bus = get_pf_grid_component(
            self, component_name=load.name
        )
        if pf_load_bus is None:
            Logger.log_to_selected(
                f"Something went wrong with the conversion of the load {load.name}, because its bus was found inside of the gdf network but not in the powerfactory network"
            )
            success = False
        else:
            pf_load.SetAttribute("bus1", pf_load_bus)

    # Set attributes for newly created load
    pf_load.SetAttribute("loc_name", load.name)
    pf_load.SetAttribute("plini", load.active_power)
    pf_load.SetAttribute("qlini", load.reactive_power)
    pf_load.SetAttribute("u0", 1)
    pf_load.SetAttribute("scale0", 1)

    return success
