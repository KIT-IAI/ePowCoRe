from epowcore.gdf.tline import TLine
from epowcore.gdf.utils import get_connected_bus
from epowcore.generic.component_graph import ComponentGraph
from epowcore.jmdl.constants import LINE_CLASS_NAME
from epowcore.jmdl.utils import clean
from epowcore.jmdl.jmdl_model import Block, Data, DataType, Layout, Port


def create_line_block(
    tline: TLine,
    graph: ComponentGraph,
    base_mva: float,
    ports: list[Port],
    geo_data: Data,
    append_uid: bool = False,
) -> Block:
    return Block(
        name=f"{clean(tline.name)}_{tline.uid}" if append_uid else clean(tline.name),
        block_type="BasicBlock",
        block_class=LINE_CLASS_NAME,
        ports=ports,
        comment="",
        url="",
        tags=["Line"],
        data=Data(
            "",
            DataType.GROUP,
            [
                Data(
                    "",
                    DataType.GROUP,
                    get_line_data(tline, graph, base_mva),
                    None,
                    None,
                    "EPowLine",
                ),
                geo_data,
            ],
            None,
            None,
            "data",
        ),
        layout=Layout(),
    )


def get_line_data(tline: TLine, graph: ComponentGraph, base_mva: float) -> list[Data]:
    connected_bus = get_connected_bus(graph, tline)
    if connected_bus is None:
        raise ValueError(f"Could not find connected bus for line {tline.uid}")
    u_base = connected_bus.nominal_voltage
    z_base = u_base**2 / base_mva
    # if no length is supplied, the impedance values are absolute
    length = tline.length if tline.length is not None else 1.0
    r1 = tline.r1 * length / z_base
    return [
        Data(
            "resistance [p.u.]",
            DataType.FLOAT64,
            [],
            r1 if r1 != 0.0 else 1e-8,
            None,
            "R",
        ),
        Data(
            "reactance [p.u.]",
            DataType.FLOAT64,
            [],
            max(1e-8, tline.x1 * length / z_base),
            None,
            "X",
        ),
        Data(
            "charging susceptance [p.u.]",
            DataType.FLOAT64,
            [],
            1e-8
            if tline.b1 == 0
            else max(
                1e-8,
                tline.b1 * 1e-6 * length * z_base,
            ),
            None,
            "B",
        ),
        Data(
            "line rating A (long term) [MVA]",
            DataType.FLOAT64,
            [],
            tline.rating,
            None,
            "rateA",
        ),
        Data(
            "line rating B (short term) [MVA]",
            DataType.FLOAT64,
            [],
            tline.rating_short_term_fb(),
            None,
            "rateB",
        ),
        Data(
            "line rating C (emergency) [MVA]",
            DataType.FLOAT64,
            [],
            tline.rating_emergency_fb(),
            None,
            "rateC",
        ),
        Data(
            "Minimum angle difference [deg]",
            DataType.FLOAT64,
            [],
            tline.get_fb("angle_min"),
            None,
            "angleMin",
        ),
        Data(
            "Maximum angle difference [deg]",
            DataType.FLOAT64,
            [],
            tline.get_fb("angle_max"),
            None,
            "angleMax",
        ),
        Data("", DataType.BOOL, [], True, None, "inService"),
        Data(
            "Amount of parallel lines of which this line consists.",
            DataType.INT64,
            [],
            tline.parallel_lines,
            None,
            "parallelLines",
        ),
    ]
