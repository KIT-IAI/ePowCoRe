import pandapower

from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import Platform
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.converter_base import ConverterBase
from epowcore.pandapower.from_gdf.pandapower_export import export_pandapower
from epowcore.pandapower.pandapower_model import PandapowerModel


class PandapowerConverter(ConverterBase[PandapowerModel]):
    def from_gdf(
        self, core_model: CoreModel, name: str, log_path: str | None = None
    ) -> PandapowerModel:
        Configuration().default_platform = Platform.PANDAPOWER
        return super().from_gdf(core_model, name, log_path)

    def _export(self, core_model: CoreModel, name: str) -> PandapowerModel:
        return export_pandapower(core_model)

    def write_to_pandapower_json(self, model: PandapowerModel, filepath: str):
        pandapower.to_json(net=model.network, filename=filepath)

    def _import(self, model):
        return model
