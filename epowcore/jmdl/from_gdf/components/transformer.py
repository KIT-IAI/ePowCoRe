from epowcore.gdf.transformers import Transformer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.jmdl.constants import TRANSFORMER_CLASS_NAME
from epowcore.jmdl.utils import clean
from epowcore.jmdl.jmdl_model import Block, Data, DataType, Layout, Port


def create_transformer_block(
    transformer: Transformer,
    base_mva: float,
    ports: list[Port],
    geo_data: Data,
    append_uid: bool = False,
) -> Block:
    return Block(
        name=f"{clean(transformer.name)}_{transformer.uid}"
        if append_uid
        else clean(transformer.name),
        block_type="BasicBlock",
        block_class=TRANSFORMER_CLASS_NAME,
        ports=ports,
        comment="",
        url="",
        tags=["Transformer"],
        data=Data(
            "",
            DataType.GROUP,
            [
                Data(
                    "MatPower transformer data.",
                    DataType.GROUP,
                    get_transformer_data(transformer, base_mva),
                    None,
                    None,
                    "EPowTransformer",
                ),
                geo_data,
            ],
            None,
            None,
            "data",
        ),
        layout=Layout(),
    )


def get_transformer_data(transformer: Transformer, base_mva: float) -> list[Data]:
    if isinstance(transformer, TwoWindingTransformer):
        return [
            Data(
                "Transformer off nominal turns ratio (tap=|V_from|/|V_to|)",
                DataType.FLOAT64,
                [],
                transformer.tap_ratio,
                None,
                "tapRatio",
            ),
            Data(
                "Transformer phase shift angle, positive => delay",
                DataType.FLOAT64,
                [],
                transformer.phase_shift,
                None,
                "phaseShift",
            ),
            Data(
                "resistance [p.u.]",
                DataType.FLOAT64,
                [],
                transformer.r1pu / transformer.rating * base_mva,
                None,
                "R",
            ),
            Data(
                "reactance [p.u.]",
                DataType.FLOAT64,
                [],
                transformer.x1pu / transformer.rating * base_mva,
                None,
                "X",
            ),
            Data(
                "charging susceptance [p.u.]",
                DataType.FLOAT64,
                [],
                transformer.bm_pu  * transformer.rating / base_mva,
                None,
                "B",
            ),
            Data(
                "Transformer rating A (long term) [MVA]",
                DataType.FLOAT64,
                [],
                transformer.rating,
                None,
                "rateA",
            ),
            Data(
                "Transformer rating B (short term) [MVA]",
                DataType.FLOAT64,
                [],
                transformer.rating_short_term_fb(),
                None,
                "rateB",
            ),
            Data(
                "Transformer rating C (emergency) [MVA]",
                DataType.FLOAT64,
                [],
                transformer.rating_emergency_fb(),
                None,
                "rateC",
            ),
            Data(
                "Minumum angle difference [deg]",
                DataType.FLOAT64,
                [],
                transformer.angle_min,
                None,
                "angleMin",
            ),
            Data(
                "Maximum angle difference [deg]",
                DataType.FLOAT64,
                [],
                transformer.angle_max,
                None,
                "angleMax",
            ),
            Data("", DataType.BOOL, [], True, None, "inService"),
        ]
    raise TypeError("Unknown transformer type!")
