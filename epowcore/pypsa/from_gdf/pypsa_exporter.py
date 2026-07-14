from typing import Callable

from pypsa import Network

from epowcore.gdf.bus import Bus
from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.logger import Logger


class PyPSAExporter:

    model_name: str
    pypsa_model: Network
    core_model: CoreModel
    method_mapping: dict[type, Callable[[Component], bool]]

    def __init__(self, core_model: CoreModel, name: str):
        self.core_model = core_model
        self.model_name = name

        self.method_mapping = {Bus: self.add_bus_from_gdf}

    def export(self):
        self.pypsa_model = Network(name=self.model_name)

        self.convert_component(Bus)

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
