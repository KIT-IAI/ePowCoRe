from typing import Callable
from epowcore.gdf.component import Component

from epowcore.jmdl.constants import (
    BUS_CLASS_NAME,
    EXTERNAL_GRID_CLASS_NAME,
    GENERATOR_CLASS_NAME,
    LINE_CLASS_NAME,
    LOAD_CLASS_NAME,
    SHUNT_CLASS_NAME,
    SWITCH_CLASS_NAME,
    TRANSFORMER_CLASS_NAME,
)
from epowcore.jmdl.jmdl_model import Block
from .bus import create_bus
from .external_grid import create_external_grid
from .generator import create_generator
from .line import create_line
from .load import create_load
from .shunt import create_shunt
from .switch import create_switch
from .transformer import create_transformer

CREATION_FUNCTION_DICT: dict[str, Callable[[Block, int], Component]] = {
    BUS_CLASS_NAME: create_bus,
    EXTERNAL_GRID_CLASS_NAME: create_external_grid,
    GENERATOR_CLASS_NAME: create_generator,
    LINE_CLASS_NAME: create_line,
    LOAD_CLASS_NAME: create_load,
    SHUNT_CLASS_NAME: create_shunt,
    SWITCH_CLASS_NAME: create_switch,
    TRANSFORMER_CLASS_NAME: create_transformer,
}
