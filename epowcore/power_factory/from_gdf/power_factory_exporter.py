import powerfactory as pf

from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.bus import Bus
from epowcore.gdf.load import Load
from epowcore.gdf.transformers import TwoWindingTransformer
from epowcore.gdf.transformers import ThreeWindingTransformer
from epowcore.power_factory.from_gdf.components.bus import create_bus
from epowcore.power_factory.from_gdf.components.load import create_load
from epowcore.power_factory.from_gdf.components.transformers import create_two_wdg_trafo
from epowcore.power_factory.from_gdf.components.transformers import create_three_wdg_trafo
from epowcore.power_factory.power_factory_model import PFModel
from epowcore.generic.logger import Logger


class PowerFactoryExporter:
    """Powerfactory exporter class responsible for converting the model,
    saving it as a file and returning a PFModel object
    """

    def __init__(self, core_model: CoreModel, name: str, app: pf.Application) -> None:
        # Get the PowerFactory Application
        if app is None:
            self.app = pf.GetApplication()
        else:
            self.app = app

        if self.app is None:
            raise ValueError("No PowerFactory Application found!")

        self.name = name
        # Create new project
        self.pf_model = self.app.CreateProject(projectName=name, gridName=name)
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

        # Converting all loads
        Logger.log_to_selected("Converting loads into the Powerfactory network")
        gdf_load_list = self.core_model.type_list(Load)

        for gdf_load in gdf_load_list:
            create_load(app=self.app, core_model=self.core_model, load=gdf_load)

        # Converting all two winding transformers
        Logger.log_to_selected("Converting two winding transformers into the Powerfactory network")
        gdf_trafo_list = self.core_model.type_list(TwoWindingTransformer)

        for gdf_trafo in gdf_trafo_list:
            create_two_wdg_trafo(app=self.app, core_model=self.core_model, trafo=gdf_trafo)

        # Converting all three winding transformers
        Logger.log_to_selected(
            "Converting three winding transformers into the Powerfactory network"
        )
        gdf_trafo_list = self.core_model.type_list(ThreeWindingTransformer)

        for gdf_trafo in gdf_trafo_list:
            create_three_wdg_trafo(app=self.app, core_model=self.core_model, trafo=gdf_trafo)

    def get_pf_model_object(self) -> PFModel:
        export_model = PFModel(
            project_name=self.name, study_case_name=None, frequency=self.core_model.base_frequency
        )
        return export_model

    def save_pf_model(self) -> None:
        cimdbexp = self.app.GetFromStudyCase("ComCimdbexp")
        result = cimdbexp.Execute()
        print(result)
