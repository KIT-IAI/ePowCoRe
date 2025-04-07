import powerfactory as pf

from epowcore.gdf.bus import Bus, BusType, LFBusType
from epowcore.generic.logger import Logger


def create_bus(app: pf.Application, bus: Bus) -> bool:
    """Convert and add the given gdf core model bus to the given powerfactory network.

    :param app: Powerfactory app object to create a new object.
    :type app: pf.Application
    :param bus: GDF core_model bus to be converted.
    :type bus: Bus
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    bus_type = {BusType.JUNCTION.value: 0, BusType.BUSBAR.value: 1, BusType.INTERNAL.value: 2}
    lf_bus_type = {
        LFBusType.PQ.value: 1,
        LFBusType.PV.value: 2,
        LFBusType.SL.value: 3,
    }
    if bus.lf_bus_type == "ISOLATED":
        Logger.log_to_selected("Cant convert bus because of lf type ISOLATED")
        return False
    # Create bus inside of network
    pf_bus = app.CreateObject("ElmTerm")
    # Set attributes for newly created bus
    pf_bus.SetAttribute("loc_name", bus.name)
    pf_bus.SetAttribute("uknom", bus.nominal_voltage)  # maybe pf-bus.uknom = ...
    pf_bus.SetAttribute("iUsage", bus_type[bus.bus_type])
    pf_bus.SetAttribute("systype", "AC")
    pf_bus.SetAttribute("busType", lf_bus_type[bus.lf_bus_type])

    return True
