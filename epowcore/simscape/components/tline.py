from math import pi
import matlab.engine
from epowcore.gdf.tline import TLine
from epowcore.gdf.core_model import CoreModel
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.PI_SECTION


def create_tline(
    eng: matlab.engine.MatlabEngine,
    tline: TLine,
    core_model: CoreModel,
    model_name: str,
) -> SimscapeBlock:
    """Create a Simscape block for the transmission line."""
    block_name = f"{model_name}/{tline.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)

    f = core_model.base_frequency
    w = 2 * pi * f

    eng.set_param(block_name, "Frequency", f"{f}", "Position", "[100 20 200 85]", nargout=0)
    if isinstance(tline, TLine):
        l1 = max(tline.x1 / w, 1e-6)
        l0 = max(tline.x0_fb() / w, 1e-6)
        c1 = max(tline.b1 / w * 1e-6, 1e-9)
        c0 = max(tline.b0_fb() / w * 1e-6, 1e-9)

        eng.set_param(
            block_name,
            "Length",
            f"{tline.get_fb('length')}",
            "Resistances",
            f"[{tline.r1:.6g},{tline.r0_fb():.6g}]",
            "Inductances",
            f"[{l1:.6g},{l0:.6g}]",
            "Capacitances",
            f"[{c1:.9g},{c0:.9g}]",
            nargout=0,
        )

    return SimscapeBlock(block_name, BLOCK_TYPE)
