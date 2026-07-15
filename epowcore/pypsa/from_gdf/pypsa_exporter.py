from typing import Callable

from pypsa import Network

from epowcore.gdf.bus import Bus
from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.load import Load
from epowcore.gdf.tline import TLine
from epowcore.gdf.utils import get_connected_bus
from epowcore.generic.logger import Logger


class PyPSAExporter:

    model_name: str
    pypsa_model: Network
    core_model: CoreModel
    method_mapping: dict[type, Callable[[Component], bool]]

    def __init__(self, core_model: CoreModel, name: str):
        self.core_model = core_model
        self.model_name = name

        self.method_mapping = {Bus: self.add_bus_from_gdf, TLine: self.add_line_from_gdf}

    def export(self):
        self.pypsa_model = Network(name=self.model_name)

        self.convert_component(Bus)
        self.convert_component(TLine)

    @staticmethod
    def export_pypsa(core_model: CoreModel, name: str) -> Network:
        exporter = PyPSAExporter(core_model=core_model, name=name)
        exporter.export()
        return exporter.pypsa_model

    def convert_component(self, component_type: type):
        Logger.log_to_selected(f"Converting {str(component_type.__name__)} components")

        component_list = self.core_model.type_list(component_type)

        for component in component_list:
            if self.method_mapping[component_type](component):
                counter += 1

        Logger.log_to_selected(
            f"Successfully converted {counter} of {len(component_list)}"
            + f" {str(component_type.__name__)} components"
        )

    def add_bus_from_gdf(self, bus: Bus) -> bool:
        name = self.pypsa_model.components.buses.add(
            name=bus.uid,
            return_names=True,
            v_nom=bus.nominal_voltage,
            type=bus.bus_type,
            x=bus.coords[0],
            y=bus.coords[1],
            carrier="AC",
            # unit
            # location
            # v_mag_pu_set=
            # v_mag_pu_min
            # v_mag_pu_max
        )
        if name != bus.id:
            return False

    def add_line_from_gdf(self, line: TLine) -> bool:

        bus0 = self.core_model.get_neighbors(component=line, follow_links=True, connector="A")
        bus1 = self.core_model.get_neighbors(component=line, follow_links=True, connector="B")

        if not bus0 or not bus1:
            Logger.log_to_selected("Conversion failed because connected busses were not found")
            return False

        name = self.pypsa_model.components.lines.add(
            name=line.uid,
            bus0=bus0.uid,
            bus1=bus1.uid,
            type="",
            x=line.x1,
            r=line.r1,
            # g=line.g,
            b=line.b1,
            s_nom=line.rating,
            # snom_mod
            # s_nom_extendable # for optimization
            # s_nom_min
            # s_nom_max # this list is not complete
            # s_nom_set
            # s_max_pu
            length=line.length,
            carrier="AC",
            num_parallel=line.parallel_lines,
            v_ang_min=line.angle_min,
            v_ang_max=line.angle_max,
        )
        if name != line.id:
            return False

    def add_load_from_gdf(self, load: Load) -> bool:
        load_bus = get_connected_bus(self.core_model.graph, load, max_depth=1)
        # If no load bus was found the function fails
        if load_bus is None:
            Logger.log_to_selected("There was no bus found connected to the load")
            return False
        sign = -1 if load.active_power >= 0 else 1
        name = self.pypsa_model.components.loads.add(
            name=load.uid,
            bus=load_bus.uid,
            type=",",
            p_set=abs(load.active_power),
            q_set=abs(load.reactive_power),
            sign=sign,
            active=True,
        )
        if name != load.id:
            return False
