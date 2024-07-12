from geojson import FeatureCollection

from epowcore.gdf.core_model import CoreModel
from epowcore.generic.converter_base import ConverterBase
from epowcore.geo_json.from_gdf.geo_json_export import export_geo_json


class GeoJSONConverter(ConverterBase[FeatureCollection]):
    def from_gdf(
        self, core_model: CoreModel, name: str, log_path: str | None = None
    ) -> FeatureCollection:
        return super().from_gdf(core_model, name, log_path)

    def _export(self, core_model: CoreModel, name: str) -> FeatureCollection:
        return export_geo_json(core_model)

    def _import(self, model: FeatureCollection) -> CoreModel:
        raise NotImplementedError()

