from epowcore.gdf.bus import Bus
from epowcore.jmdl.constants import JMDL_GDF_BUS_TYPE_DICT
from epowcore.jmdl.jmdl_model import Block
from epowcore.jmdl.utils import get_coordinates


def create_bus(block: Block, uid: int) -> Bus:
    bus_data = block.data.entries_dict["EPowBus"]
    bus_type = JMDL_GDF_BUS_TYPE_DICT[bus_data.entries_dict["busType"].value]
    return Bus(
        uid,
        block.name,
        get_coordinates(block),
        nominal_voltage=bus_data.entries_dict["baseKV"].value,
        lf_bus_type=bus_type,
    )
