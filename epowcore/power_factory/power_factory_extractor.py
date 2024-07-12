from typing import Any
import networkx as nx

import powerfactory as pf

from epowcore.gdf import DataStructure
from epowcore.gdf.component import Component
from epowcore.gdf.exciters.exciter import Exciter
from epowcore.gdf.governors.governor import Governor
from epowcore.gdf.power_system_stabilizers.power_system_stabilizer import PowerSystemStabilizer
from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.component_graph import ComponentGraph
from epowcore.generic.configuration import Configuration
from epowcore.generic.logger import Logger
import epowcore.power_factory.components as Components

import epowcore.power_factory.graph_transformer_pf as graph_transformer
from epowcore.power_factory.utils import get_coords


class PowerFactoryExtractor:
    """This class extracts the values from PowerFactory to GenericDataStructure."""

    def __init__(
        self,
        project_name: str,
        study_case_name: str | None,
        frequency: float,
        app: pf.Application | None = None,
    ) -> None:
        self._component_dict: dict[pf.DataObject, Component] = {}
        """Dictionary to map PowerFactory elements to GenericDataStructure elements"""
        self._edge_dict: dict[pf.DataObject, dict[pf.DataObject, list[str]]] = {}
        """Dictionary to map connection names to edges."""
        self.uid = 0
        """Id for the elements extracted to the datastructure"""
        self.graph = nx.Graph()
        """Graph for PowerFactory elements"""
        self.data_structure = DataStructure(base_frequency=frequency)
        """Collects the extracted values"""

        # Get the PowerFactory Application
        if app is None:
            self.app = pf.GetApplication()
        else:
            self.app = app

        if self.app is None:
            raise ValueError("No PowerFactory Application found!")

        # Activate Project
        self.app.ActivateProject(project_name)
        self.project = self.app.GetActiveProject()
        # Get studycase and activate it
        study_case_folder = self.app.GetProjectFolder("study")
        if study_case_name is not None:
            case = study_case_folder.GetContents(study_case_name + ".IntCase")[0]
            case.Activate()

        # Do a loadflow to get the correct bustype for the buses
        # and potentially for generators
        loadflow = self.app.GetFromStudyCase("ComLdf")
        loadflow.Execute()

    def get_data_structure(self) -> DataStructure:
        """Starts the extraction of elements and returns them in the GenericDataStructure format"""

        self.extract_bus(use_station_name=Configuration().get("PowerFactory.BUS_STATION_NAME"))
        self.extract_load()
        self.extract_two_winding_transformers()
        self.extract_three_winding_transformers()
        self.extract_lines()
        self.extract_synchronous_machines(
            use_load_flow=Configuration().get("PowerFactory.USE_LOAD_FLOW")
        )
        self.extract_static_generators(
            use_load_flow=Configuration().get("PowerFactory.USE_LOAD_FLOW")
        )
        self.extract_ward_equivalents()
        self.extract_impedances()
        self.extract_pv_systems()
        self.extract_external_grids()
        self.extract_switches()
        self.extract_shunts()

        self.set_data_structure_graph()
        if Configuration().get("PowerFactory.FOLDER_TO_SUBSYSTEM"):
            parents = self.get_hierarchy()

            for parent, children in parents.items():
                sub = Subsystem.from_components(
                    self.data_structure,
                    [self._component_dict[x] for x in children if x in self._component_dict],
                )
                sub.coords = get_coords(parent)

        return self.data_structure

    def get_hierarchy(self) -> dict:
        """Returns the hierarchy of the PowerFactory elements as a hierarchy."""
        parents: dict = {}
        for component in self._component_dict:
            parent = component.GetParent()
            if parent.GetClassName() not in ["ElmNet", "ElmXnet"]:
                if parent not in parents:
                    parents[parent] = []
                if not component in parents[parent]:
                    parents[parent].append(component)
        return parents

    def extract_bus(self, use_station_name: bool = False) -> None:
        """Extract the PowerFactory buses to the data format"""

        # Get the buses from the studycase
        pf_buses = self.app.GetCalcRelevantObjects("ElmTerm")
        for pf_bus in pf_buses:
            try:
                bus = Components.create_bus(pf_bus, self.uid, use_station_name)
                self.uid += 1
                # Add the mapping to dictionary and PowerFactory element to the graph
                self._component_dict[pf_bus] = bus
                self.graph.add_node(pf_bus)
            except ValueError as e:
                Logger.log_to_selected(str(e))

    def extract_load(self) -> None:
        """Extract the PowerFactory loads to the data format"""
        # Get the loads from the studycase
        pf_loads = self.app.GetCalcRelevantObjects("ElmLod")
        pf_loads_lv = self.app.GetCalcRelevantObjects("ElmLodlv")
        for pf_load in pf_loads:
            load = Components.create_load(pf_load, self.uid)
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[pf_load] = load
            self.graph.add_node(pf_load)
        for pf_load in pf_loads_lv:
            load = Components.create_load_lv(pf_load, self.uid)
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[pf_load] = load
            self.graph.add_node(pf_load)

    def extract_two_winding_transformers(self) -> None:
        """Extract the PowerFactory transformers with two windings to the data format"""
        # Get the two winding transformers from the studycase
        pf_transformers = self.app.GetCalcRelevantObjects("ElmTr2")
        for pf_transformer in pf_transformers:
            two_winding_transformer = Components.create_two_wdg_trafo(pf_transformer, self.uid)
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[pf_transformer] = two_winding_transformer
            edge_dict = {
                pf_transformer.bushv.cterm: ["HV"],
                pf_transformer.buslv.cterm: ["LV"],
            }
            self._edge_dict[pf_transformer] = edge_dict
            self.graph.add_node(pf_transformer)

    def extract_three_winding_transformers(self) -> None:
        """Extract the PowerFactory transformers with three windings to the data format"""
        # Get the three winding transformers from the studycase
        pf_transformers = self.app.GetCalcRelevantObjects("ElmTr3")
        for pf_transformer in pf_transformers:
            if pf_transformer.outserv == 1:
                continue
            three_winding_transformer = Components.create_three_wdg_trafo(pf_transformer, self.uid)
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[pf_transformer] = three_winding_transformer
            edge_dict = {
                pf_transformer.bushv.cterm: ["HV"],
                pf_transformer.busmv.cterm: ["MV"],
                pf_transformer.buslv.cterm: ["LV"],
            }
            self._edge_dict[pf_transformer] = edge_dict
            self.graph.add_node(pf_transformer)

    def extract_lines(self) -> None:
        """Extract the PowerFactory transmission lines to the data format"""
        # Get the transmission lines from the study case
        pf_tlines = self.app.GetCalcRelevantObjects("ElmLne")
        for pf_tline in pf_tlines:
            line = Components.create_tline(pf_tline, self.uid)
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[pf_tline] = line
            edge_dict = {pf_tline.bus1.cterm: ["A"], pf_tline.bus2.cterm: ["B"]}
            self._edge_dict[pf_tline] = edge_dict
            self.graph.add_node(pf_tline)

    def extract_synchronous_machines(self, use_load_flow: bool = False) -> None:
        """Extract the PowerFactory synchronous machines to the data format"""
        # Get the synchronous machines from the study case
        pf_generators = self.app.GetCalcRelevantObjects("ElmSym")
        for pf_generator in pf_generators:
            generator = Components.create_synchronous_machine(pf_generator, self.uid, use_load_flow)
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[pf_generator] = generator
            self.graph.add_node(pf_generator)
            # Call method to extract PSS, Exciter and Governor
            if pf_generator.c_pmod is not None:
                self.select_avr_type(pf_generator)
                self.select_pss_type(pf_generator)
                self.select_gov_type(pf_generator)

    def extract_static_generators(self, use_load_flow: bool = False) -> None:
        """Extract the PowerFactory static generators to the data format"""
        # Get the static generators from the study case
        pf_generators = self.app.GetCalcRelevantObjects("ElmGenStat")
        for pf_generator in pf_generators:
            generator = Components.create_static_generator(pf_generator, self.uid, use_load_flow)
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[pf_generator] = generator
            self.graph.add_node(pf_generator)

    def extract_ward_equivalents(self) -> None:
        """Extract the PowerFactory Ward equivalents to the data format"""
        pf_wards = self.app.GetCalcRelevantObjects("ElmVac")
        for pf_ward in pf_wards:
            if pf_ward.itype == 2:
                ward = Components.create_ward(pf_ward, self.uid)
                self.uid += 1
                self._component_dict[pf_ward] = ward
                self.graph.add_node(pf_ward)
            elif pf_ward.itype == 3:
                ward = Components.create_extended_ward(pf_ward, self.uid)
                self.uid += 1
                self._component_dict[pf_ward] = ward
                self.graph.add_node(pf_ward)

    def extract_impedances(self) -> None:
        """Extract the PowerFactory impedances lines to the data format"""
        pf_impedances = self.app.GetCalcRelevantObjects("ElmZpu")
        for pf_impedance in pf_impedances:
            impedance = Components.create_impedance(pf_impedance, self.uid)
            self.uid += 1
            self._component_dict[pf_impedance] = impedance
            edge_dict = {pf_impedance.bus1.cterm: ["A"], pf_impedance.bus2.cterm: ["B"]}
            self._edge_dict[pf_impedance] = edge_dict
            self.graph.add_node(pf_impedance)

    def extract_pv_systems(self) -> None:
        """Extract the PowerFactory PV systems to the data format"""
        pf_pv_systems = self.app.GetCalcRelevantObjects("ElmPvsys")
        for pf_pv_system in pf_pv_systems:
            pv_system = Components.create_pv_system(pf_pv_system, self.uid)
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[pf_pv_system] = pv_system
            self.graph.add_node(pf_pv_system)

    def extract_external_grids(self) -> None:
        """Extract the PowerFactory external grids to the data format"""
        pf_extgrids = self.app.GetCalcRelevantObjects("ElmXnet")
        for pf_extgrid in pf_extgrids:
            extgrid = Components.create_external_grid(pf_extgrid, self.uid)
            self.uid += 1
            self._component_dict[pf_extgrid] = extgrid
            self.graph.add_node(pf_extgrid)

    def extract_switches(self) -> None:
        """Extract the PowerFactory switches to the data format"""
        # pf_switches = self.app.GetCalcRelevantObjects("StaSwitch")
        # for pf_switch in pf_switches:
        #     switch = Switch.from_power_factory(pf_switch, self.uid)
        #     self.uid += 1
        #     self.transformation_dict[pf_switch] = switch
        #     self.graph.add_node(pf_switch)
        pf_switches = self.app.GetCalcRelevantObjects("ElmCoup")
        for pf_switch in pf_switches:
            switch = Components.create_switch(pf_switch, self.uid)
            self.uid += 1
            self._component_dict[pf_switch] = switch
            self.graph.add_node(pf_switch)

    def extract_shunts(self) -> None:
        """Extract the PowerFactory shunts to the data format"""
        pf_shunts = self.app.GetCalcRelevantObjects("ElmShnt")
        for pf_shunt in pf_shunts:
            shunt = Components.create_shunt(pf_shunt, self.uid)
            self.uid += 1
            self._component_dict[pf_shunt] = shunt
            self.graph.add_node(pf_shunt)

    def select_pss_type(self, generator: Any) -> None:
        """Selects one of the currently supported PSS to extract"""
        # See comment in [select_gov_type] for explanation.
        ctrl_index = _get_controller_index(generator.c_pmod.pblk, ["ElmPss"])
        if ctrl_index is None:
            raise NotImplementedError(f"Cannot find stabilizer slot for: {generator.loc_name}")
        pss = generator.c_pmod.pelm[ctrl_index]
        generic_pss: PowerSystemStabilizer | None = None
        if pss is not None:
            if "pss_CONV" in str(pss.typ_id):
                generic_pss = Components.create_ptist1(pss, self.uid)
            elif "pss_IEEE_PSS1A" in str(pss.typ_id):
                generic_pss = Components.create_ieee_pss1a(pss, self.uid)
            elif "pss_PSS2A" in str(pss.typ_id):
                generic_pss = Components.create_ieee_pss2a(pss, self.uid)
            else:
                return
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[pss] = generic_pss
            self.graph.add_node(pss)
            # Create edge with the appropriate generator
            self.graph.add_edge(pss, generator)

    def select_avr_type(self, generator: Any) -> None:
        """Selects one of the currently supported Exciter to extract"""
        # See comment in [select_gov_type] for explanation.
        ctrl_index = _get_controller_index(generator.c_pmod.pblk, ["ElmExc", "ElmAvr", "ElmVco"])
        if ctrl_index is None:
            raise NotImplementedError(f"Cannot find exciter slot for: {generator.loc_name}")
        avr = generator.c_pmod.pelm[ctrl_index]
        generic_avr: Exciter | None = None
        if avr is not None:
            avr_type = str(avr.typ_id)
            if "avr_IEEET1" in avr_type:
                generic_avr = Components.create_ieee_t1(avr, self.uid)
            elif any(s in avr_type for s in ("avr_ESST1A", "exc_IEEE_ST1A")):
                generic_avr = Components.create_ieee_st1a(avr, self.uid)
            elif "avr_SEXS" in avr_type:
                generic_avr = Components.create_sexs(avr, self.uid)
            else:
                return
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[avr] = generic_avr
            self.graph.add_node(avr)
            # Create edge with the appropriate generator
            self.graph.add_edge(avr, generator)

    def select_gov_type(self, generator: Any) -> None:
        """Selects one of the currently supported Governor to extract"""
        # PowerFactory defines the control structure of transformers in
        # so called "plant models" (c_pmod). These plant models contain the
        # controllers and a frame that defines the connections between
        # the controllers.
        # Different frame types can contain the same controller types
        # at different positions. Thus, we utilize the filter mechanic of the
        # frame to find the right slot for the desired controller.
        # pblk is a list of all of all supported blocks in the frame.

        ctrl_index = _get_controller_index(generator.c_pmod.pblk, ["ElmGov", "ElmComp", "ElmPcu"])
        if ctrl_index is None:
            raise NotImplementedError(f"Cannot find governor slot for: {generator.loc_name}")
        gov = generator.c_pmod.pelm[ctrl_index]

        if gov is not None:
            gov_type = str(gov.typ_id)
            generic_gov: Governor | None = None
            if any(s in gov_type for s in ("gov_IEEEG1", "gov_IEEE_IEEEG1")):
                generic_gov = Components.create_ieee_g1(gov, self.uid)
            elif "gov_GAST" in gov_type:
                generic_gov = Components.create_gast(gov, self.uid)
            elif "gov_HYGOV" in gov_type:
                generic_gov = Components.create_hygov(gov, self.uid)
            else:
                return
            self.uid += 1
            # Add the mapping to dictionary and PowerFactory element to the graph
            self._component_dict[gov] = generic_gov
            self.graph.add_node(gov)
            # Create edge with the appropriate generator
            self.graph.add_edge(gov, generator)

    def set_data_structure_graph(self) -> None:
        """This creates the graph for the GenericDataStructure"""
        # Create edges for PowerFactory graph
        graph_transformer.create_edges(self.graph, self._component_dict, self._edge_dict)
        # Transform PowerFactory graph to GenericDataStructure graph with the dictionary

        self.data_structure.graph = ComponentGraph(
            graph_transformer.relabel_nodes(self.graph, self._component_dict)
        )


def _get_controller_index(frame_blocks: list[pf.DataObject], extensions: list[str]) -> int | None:
    for i, block in enumerate(frame_blocks):
        for ext in extensions:
            if ext in block.filtmod:
                return i
    return None
