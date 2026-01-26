from epowcore.gdf.switch import Switch
from epowcore.power_factory.utils import get_pf_grid_component, add_cubicle_to_bus
from epowcore.generic.logger import Logger

def create_switch(self, switch: Switch) -> bool:
    """Convert and add the given gdf core model switch to the given powerfactory network.

    :param switch: GDF core_model switch to be converted.
    :type switch: Switch
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    success = True

    # Create new switch inside of grid
    pf_switch = self.pf_grid.CreateObject("ElmCoup", switch.name)

    from_bus= self.core_model.get_neighbors(component=switch, follow_links=True)[0]
    to_bus = self.core_model.get_neighbors(component=switch, follow_links=True)[1]
    if from_bus is None or to_bus is None:
        Logger.log_to_selected(
            f"At least one connection not found inside of the gdf for switch {switch.name}"
        )
        success = False

    # Get powerfactory connections
    pf_from_bus = get_pf_grid_component(self, component_name=from_bus.name)
    pf_to_bus = get_pf_grid_component(self, component_name=to_bus.name)

    if pf_from_bus is None or pf_to_bus is None:
        Logger.log_to_selected(
            f"At least one connection not found inside of powerfactory for switch {switch.name}"
        )
        success = False

    # Set connections
    pf_switch.SetAttribute("bus1", add_cubicle_to_bus(pf_from_bus))
    pf_switch.SetAttribute("bus2", add_cubicle_to_bus(pf_to_bus))
    pf_switch.SetAttribute("on_off", 1 if switch.closed else 0)
    if switch.coords is not None:
        pf_switch.GPSlon = switch.coords[1]
        pf_switch.GPSlat = switch.coords[0]

    return success