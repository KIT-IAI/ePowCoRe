import matlab.engine
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType
from epowcore.simscape.tools import sanitize_tag_name


BLOCK_TYPE = SimscapeBlockType.VI_MEASUREMENT


def create_vi_measurement(
    eng: matlab.engine.MatlabEngine,
    vi_name: str,
    model_name: str,
    add_scope: bool = False,
) -> tuple[SimscapeBlock, SimscapeBlock | None]:
    """Insert a VI measurement block into the model.

    :param eng: Matlab engine
    :param vi_name: Name of the VI measurement
    :param model_name: Name of the model
    :param add_scope: If True, a scope will be added to the VI measurement
    :return: Tuple with the VI measurement block and the scope if add_scope is True
    """
    block_name = f"{model_name}/{vi_name}"
    label_name = sanitize_tag_name(vi_name, max_length=63 - 5)
    eng.add_block(
        BLOCK_TYPE.value,
        block_name,
        "Position",
        "[500 20 520 85]",
        "VoltageMeasurement",
        "phase-to-phase",
        # "SetLabelV",
        # "on",
        "LabelV",
        f"Vabc_{label_name}",
        # "SetLabelI",
        # "on",
        "LabelI",
        f"Iabc_{label_name}",
        nargout=0,
    )

    # Add monitoring scope
    if add_scope:
        eng.add_block(SimscapeBlockType.SCOPE.value, block_name + "_Scope", nargout=0)
        eng.set_param(block_name + "_Scope", "NumInputPorts", "2", nargout=0)
        return (
            SimscapeBlock(block_name, BLOCK_TYPE),
            SimscapeBlock(block_name + "_Scope", SimscapeBlockType.SCOPE),
        )
    return (SimscapeBlock(block_name, BLOCK_TYPE), None)
