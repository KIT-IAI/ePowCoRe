from epowcore.gdf.switch import Switch
from epowcore.jmdl.constants import SWITCH_CLASS_NAME
from epowcore.jmdl.jmdl_model import Block, Data, DataType, Layout, Port
from epowcore.jmdl.utils import clean


def create_switch_block(
    switch: Switch, ports: list[Port], geo_data: Data, append_uid: bool = False
) -> Block:
    return Block(
        name=f"{clean(switch.name)}_{switch.uid}" if append_uid else clean(switch.name),
        block_type="BasicBlock",
        block_class=SWITCH_CLASS_NAME,
        ports=ports,
        comment="",
        url="",
        tags=["Switch"],
        data=Data(
            "",
            DataType.GROUP,
            [
                get_switch_data(switch),
                geo_data,
            ],
            None,
            None,
            "data",
        ),
        layout=Layout(),
    )


def get_switch_data(switch: Switch) -> Data:
    return Data(
        "",
        DataType.GROUP,
        [
            Data(
                "If set to true, the switch connects.",
                DataType.BOOL,
                [],
                switch.closed,
                None,
                "on",
            ),
            Data(
                "If set to true, the switch has no failure.",
                DataType.BOOL,
                [],
                switch.get_fb("in_service"),
                None,
                "inService",
            ),
            Data(
                "MVA rating A (long term rating)",
                DataType.FLOAT64,
                [],
                switch.get_fb("rate_a"),
                None,
                "rateA",
            ),
            Data(
                "MVA rating B (short term rating)",
                DataType.FLOAT64,
                [],
                switch.get_fb("rate_b"),
                None,
                "rateB",
            ),
            Data(
                "MVA rating C (emergency rating)",
                DataType.FLOAT64,
                [],
                switch.get_fb("rate_c"),
                None,
                "rateC",
            ),
        ],
        None,
        None,
        "EPowSwitch",
    )
