from epowcore.gdf.bus import Bus, BusType  # , LFBusType

# from epowcore.generic.logger import Logger


def create_bus(self, bus: Bus) -> bool:
    """Convert and add the given gdf core model bus to the given powerfactory network.

    :param bus: GDF core_model bus to be converted.
    :type bus: Bus
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    # Create bus inside of network
    pf_bus = self.pf_grid.CreateObject("ElmTerm")
    # Conversion of bus type
    bus_type = {BusType.BUSBAR: 0, BusType.JUNCTION: 1, BusType.INTERNAL: 2}
    # lf_bus_type = {
    #     LFBusType.PQ: 1,
    #     LFBusType.PV: 2,
    #     LFBusType.SL: 3,
    # }
    # if bus.lf_bus_type == "ISOLATED":
    #     Logger.log_to_selected(
    #         f"Bus {bus.name} can not be converted because the load flow type is ISOLATED"
    #     )
    #     return False
    # Set attributes for newly created bus
    pf_bus.SetAttribute("loc_name", bus.name)
    pf_bus.SetAttribute("uknom", bus.nominal_voltage)
    pf_bus.SetAttribute("iUsage", bus_type[bus.bus_type])
    pf_bus.SetAttribute("systype", 0)  # 0: AC
    if bus.coords is not None:
        pf_bus.GPSlon = bus.coords[1]
        pf_bus.GPSlat = bus.coords[0]
    # pf_bus.SetAttribute("busType", lf_bus_type[bus.lf_bus_type]) Unknown name of attribute
    # In import deriaved from the ElmTerm.GetBusType() function

    return True
