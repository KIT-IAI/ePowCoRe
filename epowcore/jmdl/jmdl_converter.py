import json
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import Platform
from epowcore.generic.converter_base import ConverterBase
from epowcore.jmdl.from_gdf.jmdl_export import export_jmdl
from epowcore.jmdl.to_gdf.jmdl_import import import_jmdl
from epowcore.jmdl.from_gdf.transform import transform

from epowcore.jmdl.jmdl_model import JmdlModel
from epowcore.jmdl.to_gdf.post_import import post_import


class JmdlConverter(ConverterBase[JmdlModel]):
    """Converter for easimov/JMDL files."""

    def json_to_gdf(self, json_data: str) -> CoreModel:
        """Converts the content of a JMDL file to a GDF core model."""
        jmdl = JmdlModel.from_dict(json.loads(json_data))
        return self.to_gdf(jmdl)

    def from_gdf(self, core_model: CoreModel, name: str, log_path: str | None = None) -> JmdlModel:
        Configuration().default_platform = Platform.JMDL
        return super().from_gdf(core_model, name, log_path)

    def to_gdf(self, model: JmdlModel, log_path: str | None = None) -> CoreModel:
        return super().to_gdf(model, log_path)

    def _pre_export(self, core_model: CoreModel, name: str) -> CoreModel:
        return transform(core_model)

    def _export(self, core_model: CoreModel, name: str) -> JmdlModel:
        return export_jmdl(core_model)

    def _import(self, model: JmdlModel) -> CoreModel:
        return import_jmdl(model)

    def _post_import(self, core_model: CoreModel) -> None:
        post_import(core_model)
