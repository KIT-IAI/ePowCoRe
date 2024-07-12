import json
from epowcore.gdf.data_structure import DataStructure
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

    def json_to_gdf(self, json_data: str) -> DataStructure:
        """Converts the content of a JMDL file to a GDF data structure."""
        jmdl = JmdlModel.from_dict(json.loads(json_data))
        return self.to_gdf(jmdl)

    def from_gdf(self, ds: DataStructure, name: str, log_path: str | None = None) -> JmdlModel:
        Configuration().default_platform = Platform.JMDL
        return super().from_gdf(ds, name, log_path)

    def to_gdf(self, model: JmdlModel, log_path: str | None = None) -> DataStructure:
        return super().to_gdf(model, log_path)

    def _pre_export(self, ds: DataStructure, name: str) -> DataStructure:
        return transform(ds)

    def _export(self, ds: DataStructure, name: str) -> JmdlModel:
        return export_jmdl(ds)

    def _import(self, model: JmdlModel) -> DataStructure:
        return import_jmdl(model)

    def _post_import(self, data_structure: DataStructure) -> None:
        post_import(data_structure)
