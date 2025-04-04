import powerfactory as pf

from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.bus import Bus
from epowcore.power_factory.from_gdf.components.bus import create_bus
from epowcore.power_factory.power_factory_converter import PFModel
from epowcore.generic.logger import Logger

class PowerFactoryExporter:
    """Powerfactory exporter class responsible for converting the model,
    saving it as a file and returning a PFModel object
    """
    def __init__(
            self,
            core_model: CoreModel,
            name: str,
            app: pf.Application
    ) -> None:
        # Get the PowerFactory Application
        if app is None:
            self.app = pf.GetApplication()
        else:
            self.app = app

        if self.app is None:
            raise ValueError("No PowerFactory Application found!")

        # Create new project
        self.pf_model = self.app.CreateProject(
            projectName = name,
            gridName = name
        )
        # Maybe not needed
        self.app.ActivateProject(name)

        self.core_model = core_model

    def convert_model(self) -> None:
        # Converting all buses
        Logger.log_to_selected("Creating buses in Powerfactory network")
        gdf_bus_list = self.core_model.type_list(Bus)

        # Get all attributes?
        # bus_characteristics = self.app.GetProjectFolder("chars")
        for gdf_bus in gdf_bus_list:
            create_bus(app=self.app, bus=gdf_bus)

    def get_pf_model_object(self) -> PFModel:
        return None

    def save_pf_model(self) -> None:
        return None
