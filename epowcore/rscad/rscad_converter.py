from copy import deepcopy
from pyapi_rts.api.draft import Draft
from epowcore.gdf.data_structure import DataStructure
from epowcore.generic.converter_base import ConverterBase
from epowcore.generic.manipulation.flatten import flatten
from epowcore.rscad.rscad_export import RscadExporter, RscadModel


class RscadConverter(ConverterBase[RscadModel]):
    def to_gdf(self, model: Draft, log_path: str | None = None) -> DataStructure:
        raise NotImplementedError()

    def _pre_export(self, ds: DataStructure, name: str) -> DataStructure:
        flat_ds = deepcopy(ds)
        flatten(flat_ds)
        return flat_ds

    def _export(self, ds: DataStructure, name: str) -> RscadModel:
        exporter = RscadExporter(ds)
        rscad_model = exporter.export()
        return rscad_model

    def _import(self, model: RscadModel) -> DataStructure:
        raise NotImplementedError()
