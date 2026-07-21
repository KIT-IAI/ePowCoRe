from typing import Callable

from pypsa import Network

from epowcore.gdf.bus import Bus
from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.generators import EPowGenerator, StaticGenerator, SynchronousMachine
from epowcore.gdf.load import Load
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers import TwoWindingTransformer
from epowcore.gdf.utils import get_connected_bus
from epowcore.generic.constants import Platform
from epowcore.generic.logger import Logger


class PyPSAExporter:

    model_name: str
    pypsa_model: Network
    core_model: CoreModel
    method_mapping: dict[Component, Callable[[Component], bool]]

    def __init__(self, core_model: CoreModel, name: str):
        self.core_model = core_model
        self.model_name = name

        self.method_mapping = {
            Bus: self.add_bus_from_gdf,
            TLine: self.add_line_from_gdf,
            Load: self.add_load_from_gdf,
            TwoWindingTransformer: self.add_transformer_from_gdf,
            EPowGenerator: self.add_generator_from_gdf,
            StaticGenerator: self.add_generator_from_gdf_staticgenerator,
            SynchronousMachine: self.add_generator_from_gdf_synchronousmachine,
        }

    def export(self) -> None:
        self.pypsa_model = Network(name=self.model_name)

        self.pypsa_model.components.carriers.add("AC")

        self.convert_component(Bus)
        self.convert_component(TLine)
        self.convert_component(Load)
        self.convert_component(TwoWindingTransformer)
        self.convert_component(EPowGenerator)
        self.convert_component(StaticGenerator)
        self.convert_component(SynchronousMachine)

    @staticmethod
    def export_pypsa(core_model: CoreModel, name: str) -> Network:
        exporter = PyPSAExporter(core_model=core_model, name=name)
        exporter.export()
        return exporter.pypsa_model

    def convert_component(self, component_type: type) -> None:
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
        if name != bus.uid:
            return False
        return True

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
        # PyPsa "sign" parameter defaults to -1, so it was assumed sign being -1
        # represents a normal load which consumes power
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
        if name != load.uid:
            return False
        return True

    def add_generator_from_gdf(
        self, generator: EPowGenerator | SynchronousMachine | StaticGenerator
    ) -> bool:
        generator_bus = get_connected_bus(self.core_model.graph, generator, max_depth=1)
        if generator_bus is None:
            Logger.log_to_selected(
                "Failed to convert generator because generator bus was not found"
            )
            return False

        if generator_bus.lf_bus_type.value == "ISOLATED":
            Logger.log_to_selected(
                "Conversion failed as Loadflow bus type can not be represented in generator control type"
            )
            return False

        if isinstance(generator, EPowGenerator):
            return self.add_generator_from_gdf_epowgenerator(generator, generator_bus)
        if isinstance(generator, SynchronousMachine):
            return self.add_generator_from_gdf_synchronousmachine(generator, generator_bus)
        if isinstance(generator, StaticGenerator):
            return self.add_generator_from_gdf_staticgenerator(generator, generator_bus)
        Logger.log_to_selected("Given generator does not match any ePowCoRe Generator type")
        return False

    def add_generator_from_gdf_epowgenerator(self, generator: EPowGenerator, bus: Bus) -> bool:
        self.pypsa_model.components.generators.add(
            name=generator.uid,
            bus=bus.uid,
            control=bus.lf_bus_type.value,
            type="",
            p_nom=generator.maximumRealPowerOutput,  # previously basemva
            # p_nom_mod=
            p_nom_extendable=False,  # was previously set to True with the values below
            # unsure if these should be set because they represent a change in the
            # nominal power capacity of the generator
            # p_nom_min=generator.minimumRealPowerOutput,
            # p_nom_max=generator.maximumRealPowerOutput,
            # p_nom_set=generator.realPowerOutput,
            p_min_pu=(generator.minimumRealPowerOutput / generator.maximumRealPowerOutput),
            p_max_pu=(generator.maximumRealPowerOutput / generator.maximumRealPowerOutput),
            p_set=generator.realPowerOutput,
            p_init=generator.realPowerOutput,
            q_set=generator.reactivePowerOutput,
            sign=(1 if generator.baseMVA >= 0 else -1),
            carrier=generator.category.value,
        )

    def add_generator_from_gdf_synchronousmachine(
        self, generator: SynchronousMachine, bus: Bus
    ) -> bool:
        self.pypsa_model.generators.add(
            name=generator.uid,
            bus=bus.uid,
            control=bus.lf_bus_type.value,
            type="",
            p_nom=generator.rated_active_power,
            # p_nom_mod=
            p_nom_extendable=False,  # previously set to True with the values below
            # p_nom_min=generator.p_min,
            # p_nom_max=generator.p_max,
            # p_nom_set=generator.rated_active_power,
            p_min_pu=(generator.p_min / generator.rated_active_power),
            p_max_pu=(generator.p_min / generator.rated_active_power),
            p_set=generator.active_power,
            p_init=generator.active_power,
            q_set=generator.reactive_power,
            sign=(1 if generator.rated_active_power >= 0 else -1),
            carrier=generator.category.value,
        )

    def add_generator_from_gdf_staticgenerator(self, generator: StaticGenerator, bus: Bus) -> bool:
        self.pypsa_model.generators.add(
            name=generator.uid,
            bus=bus.uid,
            control=bus.lf_bus_type.value,
            type="",
            p_nom=generator.rated_active_power,
            # p_nom_mod=
            p_nom_extendable=False,
            # p_nom_min=generator.p_min,
            # p_nom_max=generator.p_max,
            # p_nom_set=generator.rated_active_power,
            p_min_pu=(generator.p_min / generator.rated_active_power),
            p_max_pu=(generator.p_min / generator.rated_active_power),
            p_set=generator.active_power,
            p_init=generator.active_power,
            q_set=generator.reactive_power,
            sign=(1 if generator.rated_active_power >= 0 else -1),
            carrier=generator.category.value,
        )

    def add_transformer_from_gdf(self, trafo: TwoWindingTransformer) -> bool:
        # Get the bus connected to the transformer on the high voltage side
        high_voltage_bus = self.core_model.get_neighbors(
            component=trafo, follow_links=True, connector="HV"
        )
        # Get the bus connected to the transformer on the low voltage side
        low_voltage_bus = self.core_model.get_neighbors(
            component=trafo, follow_links=True, connector="LV"
        )
        if not high_voltage_bus or not low_voltage_bus:
            Logger.log_to_selected(
                "Failled to convert two winding transformer as a bus was not found"
            )
            return False
        else:
            low_voltage_bus = low_voltage_bus[0]
            high_voltage_bus = high_voltage_bus[0]

        self.pypsa_model.components.transformers.add(
            name=trafo.uid,
            bus0=high_voltage_bus.uid,
            bus1=low_voltage_bus,
            type="",
            model=trafo.get_default(attr="model", platform=Platform.PYPSA),
            x=trafo.x1pu,
            r=trafo.r1pu,
            g=trafo.gm_pu(),  # ignores other shunt loses besides magnitizing looses
            b=trafo.bm_pu(),  # ignores other shunt effects besides magnitizing effects
            s_nom=trafo.rating,
            # s_nom_mod=0,
            s_nom_extendable=False,
            # s_nom_min=
            # s_nom_max
            # s_nom_set
            s_max_pu=(
                trafo.rating / trafo.rating_short_term
            ),  # not exactly equal in meaning, could also be rating_emergency
            num_parallel=1,
            tap_ratio=trafo.tap_ratio,
            # tap_side= # unclear in epowcore
            tap_position=trafo.tap_initial,
            phase_shift=trafo.phase_shift(),
            v_ang_min=trafo.angle_min,
            v_ang_max=trafo.angle_max,
        )
