from epowcore.gdf.pv_system import PVSystem
from epowcore.power_factory.utils import get_pf_grid_component, add_cubicle_to_bus
from epowcore.generic.logger import Logger

def create_pv_system(self, pv_system: PVSystem) -> bool:
    """Convert and add the given gdf core model pv system to the given powerfactory network.

    :param pv_system: GDF core_model pv system to be converted.
    :type pv_system: PVSystem
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    success = True

    # Create new switch1 inside of grid
    pf_pv_system = self.pf_grid.CreateObject("ElmPvsys", pv_system.name)

    from_bus= self.core_model.get_neighbors(component=pv_system, follow_links=True)[0]
    if from_bus is None:
        Logger.log_to_selected(
            f"Connection not found inside of the gdf for pv_system {pv_system.name}"
        )
        success = False

    # Get powerfactory connections
    pf_from_bus = get_pf_grid_component(self, component_name=from_bus.name)

    if pf_from_bus is None:
        Logger.log_to_selected(
            f"Connection not found inside of powerfactory for pv_system {pv_system.name}"
        )
        success = False

    # Set connections
    pf_pv_system.SetAttribute("bus1", add_cubicle_to_bus(pf_from_bus))

    # PV type in PowerFactory has no values that can be set from the GDF model, therefore a standard type in the PowerFactory Library is used
    # Create new type
    pf_pv_system.SetAttribute("typ_id", self.standard_pv_type)
    pf_pv_system.SetAttribute("sgn", pv_system.rated_power/1000)
    if pv_system.coords is not None:
        pf_pv_system.GPSlon = pv_system.coords[1]
        pf_pv_system.GPSlat = pv_system.coords[0]
    # Model solar calculation
    pf_pv_system.SetAttribute("mode_pgi", 1)

    return success