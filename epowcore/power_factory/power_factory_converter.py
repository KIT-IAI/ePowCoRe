from dataclasses import dataclass

import powerfactory as pf

from epowcore.power_factory.power_factory_extractor import PowerFactoryExtractor
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.converter_base import ConverterBase


@dataclass
class PFModel:
    """A basic description for a PowerFactory project."""
    project_name: str
    study_case_name: str | None
    frequency: float


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
        raise NotImplementedError()

    def _import(self, model: PFModel) -> CoreModel:
        extractor = PowerFactoryExtractor(
            model.project_name, model.study_case_name, model.frequency, app=self.app
        )
        return extractor.get_core_model()
