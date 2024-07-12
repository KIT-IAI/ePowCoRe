from epowcore.gdf.shunt import Shunt
from epowcore.jmdl.jmdl_model import Block
from epowcore.jmdl.utils import get_coordinates


def create_shunt(block: Block, uid: int) -> Shunt:
    shunt_data = block.data.entries_dict["EPowShunt"]
    return Shunt(
        uid,
        block.name,
        get_coordinates(block),
        p=shunt_data.entries_dict["G"].value,  # Conductance (p.u.)
        q=shunt_data.entries_dict["B"].value,  # Susceptance (p.u.)
    )
