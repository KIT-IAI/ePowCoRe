import matlab.engine
from epowcore.gdf.port import Port
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType


BLOCK_TYPE_INPORT = SimscapeBlockType.INPORT
BLOCK_TYPE_OUTPORT = SimscapeBlockType.OUTPORT


def create_inport(
    eng: matlab.engine.MatlabEngine,
    port: Port,
    model_name: str,
) -> SimscapeBlock:
    """Insert an inport block into the model.

    :param eng: Matlab engine
    :param port: Port to create the inport for
    :param model_name: Name of the model
    :return: Inport block
    """
    block_name = f"{model_name}/In_{port.name}"
    eng.add_block(BLOCK_TYPE_INPORT.value, block_name, nargout=0)
    return SimscapeBlock(block_name, BLOCK_TYPE_INPORT)


def create_outport(
    eng: matlab.engine.MatlabEngine,
    port: Port,
    model_name: str,
) -> SimscapeBlock:
    """Insert an outport block into the model.

    :param eng: Matlab engine
    :param port: Port to create the outport for
    :param model_name: Name of the model
    :return: Outport block
    """

    block_name = f"{model_name}/Out_{port.name}"
    eng.add_block(BLOCK_TYPE_OUTPORT.value, block_name, nargout=0)
    return SimscapeBlock(block_name, BLOCK_TYPE_OUTPORT)
