from scipy.io import savemat

from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import Platform
from epowcore.matpower.from_gdf.matpower_export import export_matpower
from epowcore.matpower.from_gdf.transform import transform
from epowcore.matpower.matpower_model import MatpowerModel

from epowcore.gdf.core_model import CoreModel
from epowcore.generic.converter_base import ConverterBase


class MatpowerConverter(ConverterBase[MatpowerModel]):
    def from_gdf(self, core_model: CoreModel, name: str, log_path: str | None = None) -> MatpowerModel:
        Configuration().default_platform = Platform.MATPOWER
        return super().from_gdf(core_model, name, log_path)

    def write_to_matfile(self, model: MatpowerModel, file_path: str) -> None:
        savemat(file_path, model.as_dict())

    def to_gdf(self, model: MatpowerModel, log_path: str | None = None) -> CoreModel:
        raise NotImplementedError()

    def _pre_export(self, core_model: CoreModel, name: str) -> CoreModel:
        return transform(core_model)

    def _export(self, core_model: CoreModel, name: str) -> MatpowerModel:
        return export_matpower(core_model)

    def _post_export(self, model: MatpowerModel, name: str) -> MatpowerModel:
        return model
