from epowcore.gdf.external_grid import ExternalGrid
from epowcore.jmdl.constants import EXTERNAL_GRID_CLASS_NAME
from epowcore.jmdl.jmdl_model import Block, Data, DataType, Layout, Port
from epowcore.jmdl.utils import clean


def create_external_grid_block(
    external_grid: ExternalGrid,
    ports: list[Port],
    geo_data: Data,
    append_uid: bool = False,
) -> Block:
    return Block(
        name=f"{clean(external_grid.name)}_{external_grid.uid}"
        if append_uid
        else clean(external_grid.name),
        block_type="BasicBlock",
        block_class=EXTERNAL_GRID_CLASS_NAME,
        ports=ports,
        comment="",
        url="",
        tags=["ExternalGrid"],
        data=Data(
            "",
            DataType.GROUP,
            [
                Data(
                    "",
                    DataType.GROUP,
                    get_external_grid_data(external_grid),
                    None,
                    None,
                    "EPowExternalGrid",
                ),
                geo_data,
            ],
            None,
            None,
            "data",
        ),
        layout=Layout(),
    )


def get_external_grid_data(external_grid: ExternalGrid) -> list[Data]:
    return [
        Data(
            "The voltage setpoint in p.u.",
            DataType.FLOAT64,
            [],
            external_grid.u_setp,
            None,
            "V",
        ),
        Data(
            "The real power input",
            DataType.FLOAT64,
            [],
            external_grid.p,
            None,
            "P",
        ),
        Data(
            "The reactive power input",
            DataType.FLOAT64,
            [],
            external_grid.q,
            None,
            "Q",
        ),
        Data(
            "The minimum real power output",
            DataType.FLOAT64,
            [],
            external_grid.p_min,
            None,
            "Pmin",
        ),
        Data(
            "The maximum real power output",
            DataType.FLOAT64,
            [],
            external_grid.p_max,
            None,
            "Pmax",
        ),
        Data(
            "The minimum reactive power input in MVAr",
            DataType.FLOAT64,
            [],
            external_grid.q_min,
            None,
            "Qmin",
        ),
        Data(
            "The maximum reactive power input in MVAr",
            DataType.FLOAT64,
            [],
            external_grid.q_max,
            None,
            "Qmax",
        ),
        Data(
            "Determines if the external grid is defined as PQ, PV or SL(REF).",
            DataType.ENUM,
            [],
            external_grid.bus_type.value,
            "edu.kit.iai.easimov.modeler.util.ExternalGridType",
            "type",
        ),
    ]
