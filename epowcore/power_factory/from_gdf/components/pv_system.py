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
    pf_pv_system = self.pf_grid.CreateObject("ElmCoup", pv_system.name)

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

    # PV type in PowrFactory has no values that can be set from the GDF model, therefore a standard type in the PowerFactory Library is used
    # Get pv types folder --> Geht das aktuell so?
    pf_pv_type_lib = self.pf_digsilent_library.GetContents("Aleo S19.230.TypPvpanel", 1)[0]
    # Create new type
    standard_pv_panel = pf_pv_type_lib.GetContents("Aleo S19.230.TypPvpanel", 1)[0]
    pf_pv_system.SetAttribute("typ_id", standard_pv_panel)
    pf_pv_system.SetAttribute("real_power_output", pv_system.rated_power/1000)
    pf_pv_system.GPSlon = pv_system.coords[0]
    pf_pv_system.GPSlat = pv_system.coords[1]
    # Model solar calculation
    pv_system.SetAttribute("mode_pgi", 1)

    return success