import powerfactory as pf

from epowcore.gdf.bus import Bus, BusType, LFBusType
from epowcore.power_factory.utils import get_coords


def create_bus(pf_bus: pf.DataObject, uid: int, use_station_name: bool = False) -> Bus:
    """Create a bus from a PowerFactory bus object."""

    bus_name = pf_bus.loc_name if not use_station_name else pf_bus.cStatName
    lf_bus_type = _PF_LF_BUS_TYPES[pf_bus.GetBusType()]
    if lf_bus_type is None:
        raise ValueError(
            f"Bus {bus_name} has an unsupported load flow bus type: {pf_bus.GetBusType()}"
        )

    return Bus(
        uid=uid,
        name=bus_name,
        coords=get_coords(pf_bus),
        lf_bus_type=lf_bus_type,
        nominal_voltage=pf_bus.uknom,
        bus_type=_PF_BUS_TYPES[pf_bus.iUsage],
    )


_PF_LF_BUS_TYPES = (None, LFBusType.PQ, LFBusType.PV, LFBusType.SL)
_PF_BUS_TYPES = (BusType.BUSBAR, BusType.JUNCTION, BusType.INTERNAL)
