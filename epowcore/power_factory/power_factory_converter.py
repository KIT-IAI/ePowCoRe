import powerfactory as pf

from epowcore.power_factory.to_gdf.power_factory_extractor import PowerFactoryExtractor
from epowcore.power_factory.from_gdf import PowerFactoryExporter
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.converter_base import ConverterBase
from epowcore.power_factory.power_factory_model import PFModel


class PowerFactoryConverter(ConverterBase[PFModel]):
    def __init__(self, debug: bool = False) -> None:
        self.app = pf.GetApplication()
        super().__init__(debug)

    def from_gdf(self, core_model: CoreModel, name: str, log_path: str | None = None) -> PFModel:
        return super().from_gdf(core_model, name, log_path)

    def to_gdf(self, model: PFModel, log_path: str | None = None) -> CoreModel:
        """Convert a PowerFactory model to a GDF core model.

        :param model: A tuple containing the project name and the study case name.
        :param log_path: The path to the log file. If None, no log file will be created.
        """
        return super().to_gdf(model, log_path)

    def _export(self, core_model: CoreModel, name: str) -> PFModel:
        """Convert a GDF core model to a Powerfactory model.

        :param core_model: GDF core model to be converted to a Powerfactory model.
        :type core_model: CoreModel
        :param name: Name of the model
        :type name: str
        :return: _description_
        :rtype: PFModel
        """

        exporter = PowerFactoryExporter(core_model=core_model, name=name, app=self.app)
        exporter.convert_model()
        exporter.save_pf_model()
        return exporter.get_pf_model_object()

    def _import(self, model: PFModel) -> CoreModel:
        extractor = PowerFactoryExtractor(
            model.project_name, model.study_case_name, model.frequency, app=self.app
        )
        return extractor.get_core_model()
