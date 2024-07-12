import matlab.engine
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.POWERGUI


def create_powergui(eng: matlab.engine.MatlabEngine, model_name: str) -> SimscapeBlock:
    """This method adds a powergui block to the given Simscape model."""
    block_name = f"{model_name}/powergui"
    eng.add_block(BLOCK_TYPE.value, block_name, "Position", "[0 -50 80 -10]", nargout=0)

    return SimscapeBlock(block_name, BLOCK_TYPE)
