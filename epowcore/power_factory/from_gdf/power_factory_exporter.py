import powerfactory as pf

from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.bus import Bus
from epowcore.gdf.tline import TLine
from epowcore.gdf.load import Load
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.switch import Switch
from epowcore.gdf.pv_system import PVSystem
from epowcore.gdf.transformers import TwoWindingTransformer
from epowcore.gdf.transformers import ThreeWindingTransformer
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.generators.static_generator import StaticGenerator
from epowcore.power_factory.from_gdf.components.bus import create_bus
from epowcore.power_factory.from_gdf.components.line import create_line
from epowcore.power_factory.from_gdf.components.load import create_load
from epowcore.power_factory.from_gdf.components.shunt import create_shunt
from epowcore.power_factory.from_gdf.components.transformers import create_two_wdg_trafo
from epowcore.power_factory.from_gdf.components.transformers import create_three_wdg_trafo
from epowcore.power_factory.from_gdf.components.generators import create_synchronous_machine
from epowcore.power_factory.from_gdf.components.generators import create_static_generator
from epowcore.power_factory.from_gdf.components.switch import create_switch
from epowcore.power_factory.from_gdf.components.pv_system import create_pv_system
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
        self.core_model = core_model

        # Create new project
        self.pf_project = self.app.CreateProject(name, "grid")
        # Get library folders
        self.pf_library = self.app.GetProjectFolder("lib")
        self.user = self.pf_project.GetParent()
        self.database = self.user.GetParent()
        self.pf_digsilent_library = self.database.GetContents("Lib.IntLibrary")[0]
        self.pf_type_library = self.pf_project.SearchObject(
            self.pf_library.GetFullName() + "\\Equipment Type Library"
        )
        # Get grid of the powerfactory network
        self.pf_grid = self.pf_project.SearchObject(
            self.pf_project.GetFullName()
            + "\\Network Model.IntPrjfolder\\Network Data.IntPrjfolder\\grid.ElmNet"
        )

    def convert_model(self) -> None:
        # Set grid base frequency
        self.pf_grid.SetAttribute("frnom", self.core_model.base_frequency)

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

        # Creating load type folder
        pf_load_type_lib = self.pf_type_library.CreateObject("IntPrjfolder", "Load Types")
        pf_load_type_lib.iopt_typ = "equip"
        # Converting all loads
        Logger.log_to_selected("Converting loads into the Powerfactory network")
        gdf_load_list = self.core_model.type_list(Load)
        c = 0
        for gdf_load in gdf_load_list:
            if create_load(self=self, load=gdf_load):
                c += 1
        Logger.log_to_selected(f"{c} out of {len(gdf_load_list)} load creations suceeded")

        # Converting all shunts
        Logger.log_to_selected("Converting shunts into the Powerfactory network")
        gdf_shunt_list = self.core_model.type_list(Shunt)
        c = 0
        for gdf_shunt in gdf_shunt_list:
            if create_shunt(self=self, shunt=gdf_shunt):
                c += 1
        Logger.log_to_selected(f"{c} out of {len(gdf_shunt_list)} shunt creations suceeded")

        # Creating transformer type folder
        pf_trafo_type_lib = self.pf_type_library.CreateObject("IntPrjfolder", "Transformer Types")
        pf_trafo_type_lib.iopt_typ = "equip"
        # Converting all two winding transformers
        Logger.log_to_selected("Converting two winding transformers into the Powerfactory network")
        gdf_trafo_list = self.core_model.type_list(TwoWindingTransformer)
        c = 0
        for gdf_trafo in gdf_trafo_list:
            if create_two_wdg_trafo(self=self, trafo=gdf_trafo):
                c += 1
        Logger.log_to_selected(
            f"{c} out of {len(gdf_trafo_list)} two winding transformer creations suceeded"
        )

        # Converting all three winding transformers
        Logger.log_to_selected(
            "Converting three winding transformers into the Powerfactory network"
        )
        gdf_trafo_list = self.core_model.type_list(ThreeWindingTransformer)
        c = 0
        for gdf_trafo in gdf_trafo_list:
            if create_three_wdg_trafo(self=self, trafo=gdf_trafo):
                c += 1
        Logger.log_to_selected(
            f"{c} out of {len(gdf_trafo_list)} three winding transformer creations suceeded"
        )

        # Creating generator type folder
        pf_gen_type_lib = self.pf_type_library.CreateObject("IntPrjfolder", "Generator Types")
        pf_gen_type_lib.iopt_typ = "equip"

        # Converting all synchronous machines
        Logger.log_to_selected("Converting synchronous machines into powerfactory network")
        gdf_gen_list = self.core_model.type_list(SynchronousMachine)
        c = 0
        for gdf_gen in gdf_gen_list:
            if create_synchronous_machine(self, gen=gdf_gen):
                c += 1
        Logger.log_to_selected(
            f"{c} out of {len(gdf_gen_list)} synchronous machine creations suceeded"
        )

        # Converting all static generators
        Logger.log_to_selected("Converting static generators into powerfactory network")
        gdf_gen_list = self.core_model.type_list(StaticGenerator)
        c = 0
        for gdf_gen in gdf_gen_list:
            if create_static_generator(self, gen=gdf_gen):
                c += 1
        Logger.log_to_selected(
            f"{c} out of {len(gdf_gen_list)} static generator creations suceeded"
        )

        # Creating line type folder
        pf_line_type_lib = self.pf_type_library.CreateObject("IntPrjfolder", "Line Types")
        pf_line_type_lib.iopt_typ = "equip"
        # Converting all lines
        Logger.log_to_selected("Converting lines into the Powerfactory network")
        gdf_tline_list = self.core_model.type_list(TLine)
        c = 0
        for gdf_tline in gdf_tline_list:
            if create_line(self, tline=gdf_tline):
                c += 1
        Logger.log_to_selected(f"{c} out of {len(gdf_tline_list)} line creations suceeded")
        # Converting all switches
        Logger.log_to_selected("Converting switches into the Powerfactory network")
        gdf_switch_list = self.core_model.type_list(Switch)
        c = 0
        for gdf_switch in gdf_switch_list:
            if create_switch(self, switch=gdf_switch):
                c += 1
        Logger.log_to_selected(f"{c} out of {len(gdf_switch_list)} switch creations suceeded")

        # Converting all pv systems
        Logger.log_to_selected("Converting pv systems into the Powerfactory network")
        gdf_pv_system_list = self.core_model.type_list(PVSystem)
        c = 0
        for gdf_pv_system in gdf_pv_system_list:
            if create_pv_system(self, pv_system=gdf_pv_system):
                c += 1
        Logger.log_to_selected(f"{c} out of {len(gdf_pv_system_list)} pv system creations suceeded")

    def get_pf_model_object(self) -> PFModel:
        export_model = PFModel(
            project_name=self.pf_project.GetAttribute("loc_name"),
            study_case_name=self.app.GetActiveStudyCase().GetAttribute("loc_name"),
            frequency=self.pf_grid.GetAttribute("frnom"),
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
