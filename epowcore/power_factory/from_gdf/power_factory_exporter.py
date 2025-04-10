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
        self.pf_project = self.app.CreateProject(name, name + "_grid")

        self.core_model = core_model

    def convert_model(self) -> None:
        # Converting all buses
        Logger.log_to_selected("Creating buses in Powerfactory network")
        gdf_bus_list = self.core_model.type_list(Bus)
        # Get all attributes?
        # bus_characteristics = self.app.GetProjectFolder("chars")
        c = 0
        for gdf_bus in gdf_bus_list:
            if create_bus(self=self, bus=gdf_bus):
                c += 1
        Logger.log_to_selected(f"{c} out of {len(gdf_bus_list)} bus creations suceeded")

        # Converting all loads
        Logger.log_to_selected("Converting loads into the Powerfactory network")
        gdf_load_list = self.core_model.type_list(Load)
        c=0
        for gdf_load in gdf_load_list:
            if create_load(self=self, load=gdf_load):
                c += 1
        Logger.log_to_selected(f"{c} out of {len(gdf_load_list)} load creations suceeded")

        # Converting all two winding transformers
        Logger.log_to_selected("Converting two winding transformers into the Powerfactory network")
        gdf_trafo_list = self.core_model.type_list(TwoWindingTransformer)
        c=0
        for gdf_trafo in gdf_trafo_list:
            if create_two_wdg_trafo(self=self, trafo=gdf_trafo):
                c += 1
        Logger.log_to_selected(f"{c} out of {len(gdf_trafo_list)} two winding transformer creations suceeded")

        # Converting all three winding transformers
        Logger.log_to_selected(
            "Converting three winding transformers into the Powerfactory network"
        )
        gdf_trafo_list = self.core_model.type_list(ThreeWindingTransformer)
        c = 0
        for gdf_trafo in gdf_trafo_list:
            if create_three_wdg_trafo(self=self, trafo=gdf_trafo):
                c += 1
        Logger.log_to_selected(f"{c} out of {len(gdf_trafo_list)} three winding transformer creations suceeded")

    def get_pf_model_object(self) -> PFModel:
        export_model = PFModel(
            project_name=self.name, study_case_name=None, frequency=self.core_model.base_frequency
        )
        return export_model

    def save_pf_model(self) -> None:
        Logger.log_to_selected("Exporting Powerfactory Model as file")
        cimdbexp = self.app.GetFromStudyCase("ComCimdbexp")
        r = cimdbexp.Execute()
        if r == 1:
            Logger.log_to_selected("File export was sucessfull")
        else:
            Logger.log_to_selected("File export failed")
