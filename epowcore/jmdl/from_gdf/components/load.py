from epowcore.gdf.load import Load
from epowcore.jmdl.constants import LOAD_CLASS_NAME
from epowcore.jmdl.jmdl_model import Block, Data, DataType, Layout, Port
from epowcore.jmdl.utils import clean


def create_load_block(
    load: Load, ports: list[Port], geo_data: Data, append_uid: bool = False
) -> Block:
    return Block(
        name=f"{clean(load.name)}_{load.uid}" if append_uid else clean(load.name),
        block_type="BasicBlock",
        block_class=LOAD_CLASS_NAME,
        ports=ports,
        comment="",
        url="",
        tags=["Load"],
        data=Data(
            "",
            DataType.GROUP,
            [
                Data("", DataType.GROUP, get_load_data(load), None, None, "EPowLoad"),
                geo_data,
            ],
            None,
            None,
            "data",
        ),
        layout=Layout(),
    )


def get_load_data(load: Load) -> list[Data]:
    return [
        Data(
            "Real power demand",
            DataType.FLOAT64,
            [],
            load.active_power,
            None,
            "P",
        ),
        Data(
            "The reactive power demand",
            DataType.FLOAT64,
            [],
            load.reactive_power,
            None,
            "Q",
        ),
    ]
