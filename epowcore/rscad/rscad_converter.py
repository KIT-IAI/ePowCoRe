from copy import deepcopy
from pyapi_rts.api.draft import Draft
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.converter_base import ConverterBase
from epowcore.generic.manipulation.flatten import flatten
from epowcore.rscad.rscad_export import RscadExporter, RscadModel


class RscadConverter(ConverterBase[RscadModel]):
    def to_gdf(self, model: Draft, log_path: str | None = None) -> CoreModel:
        raise NotImplementedError()

    def _pre_export(self, core_model: CoreModel, name: str) -> CoreModel:
        flat_ds = deepcopy(core_model)
        flatten(flat_ds)
        return flat_ds

    def _export(self, core_model: CoreModel, name: str) -> RscadModel:
        exporter = RscadExporter(core_model)
        rscad_model = exporter.export()
        return rscad_model

    def _import(self, model: RscadModel) -> CoreModel:
        raise NotImplementedError()
