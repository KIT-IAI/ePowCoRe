from epowcore.gdf.external_grid import ExternalGrid
from epowcore.power_factory.utils import get_pf_grid_component, add_cubicle_to_bus
from epowcore.generic.logger import Logger
from epowcore.gdf.external_grid import ExternalGridType

def create_external_grid(self, external_grid: ExternalGrid) -> bool:
    """Convert and add the given gdf core model external grid to the given powerfactory network.

    :param external_grid: GDF core_model external grid to be converted.
    :type external_grid: ExternalGrid
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    success = True

    # Create new switch inside of grid
    pf_external_grid = self.pf_grid.CreateObject("ElmXnet", external_grid.name)

    connection = self.core_model.get_neighbors(component=external_grid, follow_links=True)[0]
    if connection  is None:
        Logger.log_to_selected(
            f"Connection not found inside of the gdf for external grid {external_grid.name}"
        )
        success = False

    # Get powerfactory connections
    pf_connection = get_pf_grid_component(self, component_name=connection.name)

    if pf_connection is None:
        Logger.log_to_selected(
            f"Connection not found inside of powerfactory for external grid {external_grid.name}"
        )
        success = False

    # Set connections
    pf_external_grid.SetAttribute("bus1", add_cubicle_to_bus(pf_connection))
    pf_external_grid.loc_name = external_grid.name
    pf_external_grid.usetp = external_grid.u_setp
    pf_external_grid.pgini = external_grid.p
    pf_external_grid.qgini = external_grid.q
    pf_external_grid.cQ_min = external_grid.q_min
    pf_external_grid.cQ_max = external_grid.q_max
    pf_external_grid.bustp =  external_grid.bus_type.value
    if external_grid.coords is not None:
        pf_external_grid.GPSlon = external_grid.coords[1]
        pf_external_grid.GPSlat = external_grid.coords[0]

    return success