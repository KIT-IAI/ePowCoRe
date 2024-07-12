from epowcore.gdf.switch import Switch
from epowcore.jmdl.jmdl_model import Block
from epowcore.jmdl.utils import get_coordinates


def create_switch(block: Block, uid: int) -> Switch:
    switch_data = block.data.entries_dict["EPowSwitch"]
    return Switch(
        uid,
        block.name,
        coords=get_coordinates(block),
        closed=switch_data.entries_dict["on"].value,
        in_service=switch_data.entries_dict["inService"].value,
        rate_a=switch_data.entries_dict["rateA"].value,
        rate_b=switch_data.entries_dict["rateB"].value,
        rate_c=switch_data.entries_dict["rateC"].value,
    )
