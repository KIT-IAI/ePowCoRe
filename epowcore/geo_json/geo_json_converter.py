from geojson import FeatureCollection

from epowcore.gdf.data_structure import DataStructure
from epowcore.generic.converter_base import ConverterBase
from epowcore.geo_json.from_gdf.geo_json_export import export_geo_json


class GeoJSONConverter(ConverterBase[FeatureCollection]):
    def from_gdf(
        self, ds: DataStructure, name: str, log_path: str | None = None
    ) -> FeatureCollection:
        return super().from_gdf(ds, name, log_path)

    def _export(self, ds: DataStructure, name: str) -> FeatureCollection:
        return export_geo_json(ds)

    def _import(self, model: FeatureCollection) -> DataStructure:
        raise NotImplementedError()

