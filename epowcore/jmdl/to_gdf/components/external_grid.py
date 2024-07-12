from epowcore.gdf.external_grid import ExternalGrid, ExternalGridType
from epowcore.jmdl.jmdl_model import Block
from epowcore.jmdl.utils import get_coordinates


def create_external_grid(block: Block, uid: int) -> ExternalGrid:
    grid_data = block.data.entries_dict["EPowExternalGrid"]
    return ExternalGrid(
        uid,
        block.name,
        get_coordinates(block),
        u_setp=grid_data.entries_dict["V"].value,
        p=grid_data.entries_dict["P"].value,
        q=grid_data.entries_dict["Q"].value,
        p_min=grid_data.entries_dict["Pmin"].value,
        p_max=grid_data.entries_dict["Pmax"].value,
        q_min=grid_data.entries_dict["Qmin"].value,
        q_max=grid_data.entries_dict["Qmax"].value,
        bus_type=ExternalGridType[grid_data.entries_dict["type"].value],
    )
