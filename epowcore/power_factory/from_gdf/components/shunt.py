from epowcore.gdf.shunt import Shunt
from epowcore.power_factory.utils import get_pf_grid_component, add_cubicle_to_bus
from epowcore.gdf.utils import get_connected_bus
from epowcore.generic.logger import Logger


def create_shunt(self, shunt: Shunt) -> bool:
    """Convert and add the give ngdf core model shunt to the given powerfactory network.

    :param shunt: GDF core_model shunt to be converted.
    :type shunt: Shunt
    :return: Return true if the conversion succeded, false if it didn't.
    :rtype: bool
    """
    success = True

    # Create shunt inside the pf network
    pf_shunt = self.pf_grid.CreateObject("ElmShnt")

    # Get connected bus
    gdf_shunt_bus = get_connected_bus(graph=self.core_model.graph, node=shunt, max_depth=1)
    # Check if the connected bus exists
    if gdf_shunt_bus is None:
        Logger.log_to_selected(
            f"There was no shunt bus found inside of the core_model network for the load {shunt.name}"
        )
        success = False
    else:
        # Find the power factory bus with the same name
        pf_shunt_bus = get_pf_grid_component(self, component_name=gdf_shunt_bus.name)
        if pf_shunt_bus is None:
            Logger.log_to_selected(
                f"Something went wrong with the conversion of the shunt {shunt.name}, because its bus was found inside of the gdf network but not in the powerfactory network"
            )
            success = False
        else:
            pf_shunt.SetAttribute("bus1", add_cubicle_to_bus(pf_shunt_bus))

        
    # Set attributes for newly created shunt
    pf_shunt.SetAttribute("loc_name", shunt.name)
    pf_shunt.SetAttribute("e:Qact", shunt.q)


    return success