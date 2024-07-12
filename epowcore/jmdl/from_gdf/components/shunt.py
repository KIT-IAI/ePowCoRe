from epowcore.gdf.shunt import Shunt
from epowcore.jmdl.constants import SHUNT_CLASS_NAME
from epowcore.jmdl.jmdl_model import Block, Data, DataType, Layout, Port
from epowcore.jmdl.utils import clean


def create_shunt_block(
    shunt: Shunt, ports: list[Port], geo_data: Data, append_uid: bool = False
) -> Block:
    return Block(
        name=f"{clean(shunt.name)}_{shunt.uid}" if append_uid else clean(shunt.name),
        block_type="BasicBlock",
        block_class=SHUNT_CLASS_NAME,
        ports=ports,
        comment="",
        url="",
        tags=["Shunt"],
        data=Data(
            "",
            DataType.GROUP,
            [
                Data(
                    "",
                    DataType.GROUP,
                    get_shunt_data(shunt),
                    None,
                    None,
                    "EPowShunt",
                ),
                geo_data,
            ],
            None,
            None,
            "data",
        ),
        layout=Layout(),
    )


def get_shunt_data(shunt: Shunt) -> list[Data]:
    return [
        Data(
            "The shunt conductance (MW demand at V = 1.0 p.u.",
            DataType.FLOAT64,
            [],
            shunt.p,
            None,
            "G",
        ),
        Data(
            "The shunt susceptance (MVAr injected at V = 1.0 p.u.",
            DataType.FLOAT64,
            [],
            shunt.q * -1,
            None,
            "B",
        ),
    ]
