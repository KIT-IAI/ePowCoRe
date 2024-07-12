from epowcore.gdf.load import Load
from epowcore.jmdl.jmdl_model import Block
from epowcore.jmdl.utils import get_coordinates


def create_load(block: Block, uid: int) -> Load:
    load_data = block.data.entries_dict["EPowLoad"]
    return Load(
        uid,
        block.name,
        get_coordinates(block),
        active_power=load_data.entries_dict["P"].value,
        reactive_power=load_data.entries_dict["Q"].value,
    )
