from copy import deepcopy

from epowcore.gdf.core_model import CoreModel
from epowcore.generic.manipulation.flatten import flatten
from epowcore.gdf.bus import Bus
from epowcore.gdf.load import Load
from epowcore.generic.logger import Logger

WHITE_LIST = (
    Bus,
    Load
)

def _pre_export(core_model: CoreModel) -> CoreModel:
    '''Pre export modification done to the CoreModel to make it compatible to Pandapower'''

    # Pandapower does not support subsystems, thus it is easier to work with a flattened model.
    Logger.log_to_selected("Flattening the Core Model")
    core_model_pre_export = deepcopy(core_model)
    flatten(core_model_pre_export)

    return core_model_pre_export
