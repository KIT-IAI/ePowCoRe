import powerfactory as pf

from epowcore.gdf.load import Load
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.logger import Logger


def create_load(app: pf.Application, load: Load, core_model: CoreModel) -> bool:
    """Convert and add the given gdf core model load to the given powerfactory network.

    :param app: Powerfactory app object to create a new object.
    :type app: pf.Application
    :param load: GDF core_model load to be converted.
    :type load: Load
    :param core_model: GDF core_model used to search the load bus.
    :type core_model: CoreModel
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    # Get connected bus
    # Maybe change this so the load gets converted without a connected bus if it is not found?
    neighbors = core_model.get_neighbors(component=load, follow_links=True)
    neighbors = [x for x in neighbors if isinstance(x, load)]
    # Check if connected bus exists
    if len(neighbors) < 1:
        Logger.log_to_selected(
            f"Load {load.name} was not converted, because no connected bus was found in the gdf model"
        )
        return False
    # Find the power factory bus with the same name
    pf_buses = app.GetCalcRelevantObjects("ElmTerm")
    pf_load_bus = None
    for pf_bus in pf_buses:
        if pf_bus.loc_name == neighbors[0].name:
            pf_load_bus = pf_bus
            break
    if pf_load_bus is None:
        Logger.log_to_selected(
            f"Load {load.name} can not be converted, because the load bus found in the gdf model wasn't correctly converted"
        )
        return False

    # Create load inside of network
    pf_load = app.CreateObject("ElmLod")
    # Set attributes for newly created load
    pf_load.SetAttribute("loc_name", load.name)
    pf_load.SetAttribute("bus_1", pf_load_bus)
    pf_load.SetAttribute("plini", load.active_power)
    pf_load.SetAttribute("qlini", load.reactive_power)
    pf_load.SetAttribute("u0", 1)
    pf_load.SetAttribute("scale0", 1)
