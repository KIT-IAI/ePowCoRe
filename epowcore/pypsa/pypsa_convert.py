import pypsa
from pypsa import network as pypsa_network

from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.transformers import ThreeWindingTransformer
from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import Platform
from epowcore.generic.converter_base import ConverterBase
from epowcore.pypsa.from_gdf.pypsa_exporter import PyPSAExporter


class PyPSAConverter(ConverterBase[pypsa_network]):
    def from_gdf(
        self, core_model: CoreModel, name: str, log_path: str | None = None
    ) -> pypsa_network:
        Configuration().default_platform = Platform.PYPSA
        return super().from_gdf(core_model, name, log_path)

    def _pre_export(self, core_model: CoreModel, name: str) -> CoreModel:

        # Replace all three winding transformers as they are not supported by pypsa
        three_winding_transformers = core_model.type_list(ThreeWindingTransformer)
        for trafo in three_winding_transformers:
            trafo.replace_with_two_winding_transformers(core_model)

        return core_model

    def _export(self, core_model: CoreModel, name: str) -> pypsa_network:
        return PyPSAExporter.export_pypsa(core_model=core_model, name=name)

    def to_gdf(self, model: pypsa_network, log_path: str | None = None) -> CoreModel:
        return NotImplementedError
