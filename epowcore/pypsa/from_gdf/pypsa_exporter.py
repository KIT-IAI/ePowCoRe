"""Module responsible for PyPSA export process, stores the PyPSAExporter class"""

from typing import Callable, TypeVar

import pypsa
from pypsa import Network

from epowcore.gdf.bus import Bus
from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.external_grid import ExternalGrid
from epowcore.gdf.generators import EPowGenerator, StaticGenerator, SynchronousMachine
from epowcore.gdf.load import Load
from epowcore.gdf.pv_system import PVSystem
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers import TwoWindingTransformer
from epowcore.gdf.utils import get_connected_bus, get_z_base
from epowcore.gdf.voltage_source import VoltageSource
from epowcore.generic.constants import Platform
from epowcore.generic.logger import Logger

C = TypeVar("C", bound=Component)


class PyPSAExporter:
    """Class responsible for exporting from GDF to PyPSA"""

    model_name: str
    """Name of the model being exported"""
    pypsa_model: Network
    """Conversion target PyPSA model being built"""
    core_model: CoreModel
    """Conversion source GDF model being read and converted to PyPSA"""
    method_mapping: dict[type, Callable[[Component], bool]]
    """Mapping from GDF component type to conversion method"""

    def __init__(self, core_model: CoreModel, name: str):
        pypsa.set_option("params.add.return_names", True)

        self.core_model = core_model
        self.model_name = name

        self.method_mapping = {
            Bus: self.add_bus_from_gdf,
            TLine: self.add_line_from_gdf,
            Load: self.add_load_from_gdf,
            TwoWindingTransformer: self.add_transformer_from_gdf,
            EPowGenerator: self.add_generator_from_gdf,
            StaticGenerator: self.add_generator_from_gdf,
            SynchronousMachine: self.add_generator_from_gdf,
            Shunt: self.add_shunt_from_gdf,
            PVSystem: self.add_generator_from_gdf,
            ExternalGrid: self.add_generator_from_gdf,
        }

    def export(self) -> None:
        """Export method responsible for the general export
        process, calling all included methods
        """

        self.pypsa_model = Network(name=self.model_name)

        self.pypsa_model.components.carriers.add("AC")
        self.pypsa_model.components.carriers.add("solar")

        self.convert_component(Bus)
        self.convert_component(TLine)
        self.convert_component(Load)
        self.convert_component(TwoWindingTransformer)
        self.convert_component(EPowGenerator)
        self.convert_component(StaticGenerator)
        self.convert_component(SynchronousMachine)
        self.convert_component(Shunt)
        self.convert_component(PVSystem)
        self.convert_component(ExternalGrid)

    @staticmethod
    def export_pypsa(core_model: CoreModel, name: str) -> Network:
        """Static method as outside API for export process.

        During this process, the method creates a PyPSAExporter Object, calls is export method
        and returns its converted PyPSA model.

        :param core_model: GDF model to be exported to PyPSA
        :type core_model: CoreModel
        :param name: Name of the model
        :type name: str
        :return: Exported PyPSA model converted from the GDF model
        :rtype: Network
        """
        Logger.log_to_selected("Starting PyPSA Export")
        exporter = PyPSAExporter(core_model=core_model, name=name)
        exporter.export()
        Logger.log_to_selected("PyPSA Export finished")
        return exporter.pypsa_model

    def convert_component(self, component_type: type[C]) -> None:
        """Generic method to convert a certain component type.

        This method takes a GDF component type,
        retrieves all components of the type from the GDF model and calls the conversion method
        mapped to the type in the method_mapping for each component.
        How many components of the type are sucessfully converted is automatically logged.

        :param component_type: GDF component type of which all components should be converted
        :type component_type: type
        """
        Logger.log_to_selected(f"Converting {str(component_type.__name__)} components")

        component_list: list[C] = self.core_model.type_list(component_type)
        counter = 0

        for component in component_list:
            if self.method_mapping[component_type](component):
                counter += 1

        Logger.log_to_selected(
            f"successfuly converted {counter} of {len(component_list)}"
            + f" {str(component_type.__name__)} components"
        )

    def add_bus_from_gdf(self, bus: Bus) -> bool:
        """Method for converting GDF bus components to PyPSA bus components.

        :param bus: GDF bus to convert
        :type bus: Bus
        :return: True if sucessfull else false
        :rtype: bool
        """

        bus_x = bus.coords[0] if not bus.coords is None else None
        bus_y = bus.coords[1] if not bus.coords is None else None

        bus_name = self.pypsa_model.components.buses.add(
            name=bus.uid,
            return_names=True,
            v_nom=bus.nominal_voltage,
            type=bus.bus_type,
            x=bus_x,
            y=bus_y,
            carrier="AC",
        )
        creation_result = bus_name[0] in self.pypsa_model.components.buses.static.index
        if not creation_result:
            Logger.log_to_selected(f"Creation in PyPSA failed for Bus {bus.uid}")
        return creation_result

    def add_line_from_gdf(self, line: TLine) -> bool:
        """Method for converting GDF TLine components to PyPSA line components.

        :param line: GDF TLine to convert
        :type line: TLine
        :return: True if successful else false
        :rtype: bool
        """

        bus0_list = self.core_model.get_neighbors(component=line, follow_links=True, connector="A")
        bus1_list = self.core_model.get_neighbors(component=line, follow_links=True, connector="B")

        if not bus0_list or not bus1_list:
            Logger.log_to_selected(
                f"Conversion of line (uid {line.uid}) failed because a connected bus not found"
            )
            return False

        bus0 = bus0_list[0]
        bus1 = bus1_list[0]

        line_name = self.pypsa_model.components.lines.add(
            name=line.uid,
            return_names=True,
            bus0=bus0.uid,
            bus1=bus1.uid,
            type="",
            x=line.x1 * (line.length if not line.length is None else 1),
            r=line.r1 * (line.length if not line.length is None else 1),
            b=line.b1 * (line.length if not line.length is None else 1) / 10e6,
            s_nom=line.rating,
            length=line.length,
            carrier="AC",
            num_parallel=line.parallel_lines,
            v_ang_min=line.angle_min,
            v_ang_max=line.angle_max,
        )
        creation_result = line_name[0] in self.pypsa_model.components.lines.static.index
        if not creation_result:
            Logger.log_to_selected(f"Creation in PyPSA failed for TLine {line.uid}")
        return creation_result

    def add_load_from_gdf(self, load: Load) -> bool:
        """Method for convering GDF load components to PyPSA load components.

        :param load: GDF load to convert
        :type load: Load
        :return: True if successful else false
        :rtype: bool
        """
        load_bus = get_connected_bus(self.core_model.graph, load, max_depth=1)
        # If no load bus was found the function fails
        if load_bus is None:
            Logger.log_to_selected(
                f"Conversion of the load (uid {load.uid} failed"
                + " because its connected bus was not found)"
            )
            return False
        # PyPsa "sign" parameter defaults to -1, so it was assumed sign being -1
        # represents a normal load which consumes power
        sign = -1 if load.active_power >= 0 else 1

        load_name = self.pypsa_model.components.loads.add(
            name=load.uid,
            bus=load_bus.uid,
            type="",
            p_set=abs(load.active_power),
            q_set=abs(load.reactive_power),
            sign=sign,
            active=True,
        )
        creation_result = load_name[0] in self.pypsa_model.components.loads.static.index
        if not creation_result:
            Logger.log_to_selected(f"Creation in PyPSA failed for Load {load.uid}")
        return creation_result

    def add_generator_from_gdf(
        self,
        generator: EPowGenerator | SynchronousMachine | StaticGenerator | PVSystem | ExternalGrid,
    ) -> bool:
        """Method for converting any type of GDF generator to a PyPSA generator.
        For this, the method retrieved the connected bus and calls sub methods,
        depending on the type of the given GDF generator.

        :param generator: GDF generator of some kind to convert to PyPSA
        :type generator: EPowGenerator | SynchronousMachine | StaticGenerator
        :return: True if successful else false
        :rtype: bool
        """
        generator_bus = get_connected_bus(self.core_model.graph, generator, max_depth=1)
        if generator_bus is None:
            Logger.log_to_selected(
                f"Conversion of the generator (uid {generator.uid}) failed"
                + " because generator bus was not found"
            )
            return False

        if generator_bus.lf_bus_type.value == "ISOLATED":
            Logger.log_to_selected(
                f"Conversion of the generator (uid {generator.uid}) failed because the 'ISOLATED'"
                + " bus loadflow-type cannot be represented by the PyPSA generator control type"
            )
            return False

        if isinstance(generator, EPowGenerator):
            return self.add_generator_from_gdf_epowgenerator(generator=generator, bus=generator_bus)
        elif isinstance(generator, SynchronousMachine):
            return self.add_generator_from_gdf_synchronousmachine(
                generator=generator, bus=generator_bus
            )
        elif isinstance(generator, StaticGenerator):
            return self.add_generator_from_gdf_staticgenerator(
                generator=generator, bus=generator_bus
            )
        elif isinstance(generator, PVSystem):
            return self.add_generator_from_gdf_pvsystem(pvsystem=generator, bus=generator_bus)
        elif isinstance(generator, ExternalGrid):
            return self.add_generator_from_gdf_external_grid(
                external_grid=generator, bus=generator_bus
            )
        Logger.log_to_selected(
            f"The given generator (uid {generator.uid}) does not match any ePowCoRe generator type"
        )
        return False

    def add_generator_from_gdf_epowgenerator(self, generator: EPowGenerator, bus: Bus) -> bool:
        """Method responsible for converting a GDF EPowGenerator.
        This method takes the connected bus and the EPowGenerator instance and creates
        a equal PyPSA generator which is connected to the PyPSA bus representing the
        given GDF bus.

        :param generator: GDF EPowGenerator to convert to PyPSA
        :type generator: EPowGenerator
        :param bus: GDF bus connected to the given generator
        :type bus: Bus
        :return: True if successful else false
        :rtype: bool
        """
        generator_name = self.pypsa_model.components.generators.add(
            name=generator.uid,
            bus=bus.uid,
            control=(bus.lf_bus_type.value if bus.lf_bus_type.value != "SLACK" else "Slack"),
            type="",
            p_nom=generator.maximumRealPowerOutput,
            p_min_pu=(generator.minimumRealPowerOutput / generator.maximumRealPowerOutput),
            p_max_pu=(generator.maximumRealPowerOutput / generator.maximumRealPowerOutput),
            p_set=generator.realPowerOutput,
            p_init=generator.realPowerOutput,
            q_set=generator.reactivePowerOutput,
            sign=(1 if generator.baseMVA >= 0 else -1),
            carrier=generator.category.value,
        )
        creation_result = generator_name[0] in self.pypsa_model.components.generators.static.index
        if not creation_result:
            Logger.log_to_selected(f"Creation in PyPSA failed for EPowGenerator {generator.uid}")
        return creation_result

    def add_generator_from_gdf_synchronousmachine(
        self, generator: SynchronousMachine, bus: Bus
    ) -> bool:
        """Method responsible for converting a GDF SynchronousMachine.
        This method takes the connected bus and the SynchronousMachine instance and creates
        a equal PyPSA generator which is connected to the PyPSA bus representing the
        given GDF bus.

        :param generator: GDF SynchronousMachine to convert to PyPSA
        :type generator: SynchronousMachine
        :param bus: GDF bus connected to the given generator
        :type bus: Bus
        :return: True if successful else false
        :rtype: bool
        """

        generator_name = self.pypsa_model.components.generators.add(
            name=generator.uid,
            bus=bus.uid,
            control=(bus.lf_bus_type.value if bus.lf_bus_type.value != "SLACK" else "Slack"),
            type="",
            p_nom=generator.rated_active_power,
            p_min_pu=(
                (generator.p_min / generator.rated_active_power)
                if generator.rated_active_power != 0
                else 0
            ),
            p_max_pu=(
                (generator.p_max / generator.rated_active_power)
                if generator.rated_active_power != 0
                else 0
            ),
            p_set=generator.active_power,
            p_init=generator.active_power,
            q_set=generator.reactive_power,
            sign=(1 if generator.rated_active_power >= 0 else -1),
            # carrier=generator.category.value,
        )
        creation_result = generator_name[0] in self.pypsa_model.components.generators.static.index
        if not creation_result:
            Logger.log_to_selected(
                f"Creation in PyPSA failed for SynchronousMachine {generator.uid}"
            )
        return creation_result

    def add_generator_from_gdf_staticgenerator(self, generator: StaticGenerator, bus: Bus) -> bool:
        """Method responsible for converting a GDF StaticGenerator.
        This method takes the connected bus and the StaticGenerator instance and creates
        a equal PyPSA generator which is connected to the PyPSA bus representing the
        given GDF bus.

        :param generator: GDF StaticGenerator to convert to PyPSA
        :type generator: StaticGenerator
        :param bus: GDF bus connected to the given generator
        :type bus: Bus
        :return: True if successful else false
        :rtype: bool
        """
        generator_name = self.pypsa_model.components.generators.add(
            name=generator.uid,
            bus=bus.uid,
            control=(bus.lf_bus_type.value if bus.lf_bus_type.value != "SLACK" else "Slack"),
            type="",
            p_nom=generator.rated_active_power,
            p_min_pu=(generator.p_min / generator.rated_active_power),
            p_max_pu=(generator.p_min / generator.rated_active_power),
            p_set=generator.active_power,
            p_init=generator.active_power,
            q_set=generator.reactive_power,
            sign=(1 if generator.rated_active_power >= 0 else -1),
            carrier=generator.category.value,
        )
        creation_result = generator_name[0] in self.pypsa_model.components.generators.static.index
        if not creation_result:
            Logger.log_to_selected(f"Creation in PyPSA failed for StaticGenerator {generator.uid}")
        return creation_result

    def add_generator_from_gdf_pvsystem(self, pvsystem: PVSystem, bus: Bus) -> bool:
        """Method responsible for converting a GDF PVSystem.
        This method takes the connected bus and the PVSystem instance and creates
        a equal PyPSA generator which is connected to the PyPSA bus representing the
        given GDF bus.

        :param pvsystem: GDF PVSystem to converto PyPSA
        :type pvsystem: PVSystem
        :param bus: GDF bus connected to the given PVSystem
        :type bus: Bus
        :return: True if successful else false
        :rtype: bool
        """
        # Maybe a custom constraint for the reactive power should be added
        # as pypsa does not feature and min and max reactive power

        nominal_power = pvsystem.rated_power * pvsystem.get_default(
            attr="power_factor", platform=Platform.PYPSA
        )
        Logger.log_to_selected(
            "Used default power_factor to calculate nominal power of PVSystem from its rated power"
        )

        pvsystem_name = self.pypsa_model.components.generators.add(
            name=pvsystem.uid,
            bus=bus.uid,
            p_nom=nominal_power,
            control=(bus.lf_bus_type.value if bus.lf_bus_type.value != "SLACK" else "Slack"),
            p_nom_extendable=False,
            p_min_pu=pvsystem.minimum_real_power_output / nominal_power,
            p_max_pu=pvsystem.maximum_real_power_output / nominal_power,
            p_set=pvsystem.real_power_output,
            q_set=pvsystem.reactive_power_output,
            carrier="solar",
            sign=1,
        )

        creation_result = pvsystem_name[0] in self.pypsa_model.components.generators.static.index
        if not creation_result:
            Logger.log_to_selected(f"Creation in PyPSA failed for PVSystem {pvsystem.uid}")
        return creation_result

    def add_generator_from_gdf_external_grid(self, external_grid: ExternalGrid, bus: Bus) -> bool:
        """Method responsible for converting a GDF ExternalGrid.
        This method takes the connected bus and the ExternalGrid instance and creates
        a equal PyPSA generator which is connected to the PyPSA bus representing the
        given GDF bus.

        :param external_grid: _description_
        :type external_grid: ExternalGrid
        :param bus: GDF bus connected to the given ExternalGrid
        :type bus: Bus
        :return: True if successful else false
        :rtype: bool
        """

        # Maybe a custom constraint for the reactive power should be added
        # as pypsa does not feature and min and max reactive power

        external_grid_name = self.pypsa_model.components.generators.add(
            name=external_grid.uid,
            bus=bus.uid,
            control=(
                external_grid.bus_type.value if external_grid.bus_type.value != "SL" else "Slack"
            ),
            p_nom_extendable=False,
            p_min_pu=(
                (external_grid.p_min / external_grid.p) if not external_grid.p_min is None else None
            ),
            p_max_pu=(
                (external_grid.p_max / external_grid.p) if not external_grid.p_max is None else None
            ),
            p_set=external_grid.p,
            q_set=external_grid.q,
        )

        creation_result = (
            external_grid_name[0] in self.pypsa_model.components.generators.static.index
        )
        if not creation_result:
            Logger.log_to_selected(f"Creation in PyPSA failed for ExternalGrid {external_grid.uid}")
        return creation_result

    def add_transformer_from_gdf(self, trafo: TwoWindingTransformer) -> bool:
        """Method for converting GDF TwoWindingTransformer components
        to PyPSA transformer components.

        :param trafo: GDF TwoWindingTransformer to convert
        :type trafo: TwoWindingTransformer
        :return: True if succesful else False
        :rtype: bool
        """
        # Get the bus connected to the transformer on the high voltage side
        high_voltage_bus_list = self.core_model.get_neighbors(
            component=trafo, follow_links=True, connector="HV"
        )
        # Get the bus connected to the transformer on the low voltage side
        low_voltage_bus_list = self.core_model.get_neighbors(
            component=trafo, follow_links=True, connector="LV"
        )
        if not high_voltage_bus_list or not low_voltage_bus_list:
            Logger.log_to_selected(
                f"Conversion of TwoWindingTransformer (uid {trafo.uid}) because"
                + " a connected bus was not found"
            )
            return False
        low_voltage_bus = low_voltage_bus_list[0]
        high_voltage_bus = high_voltage_bus_list[0]

        trafo_name = self.pypsa_model.components.transformers.add(
            name=trafo.uid,
            bus0=high_voltage_bus.uid,
            bus1=low_voltage_bus.uid,
            type="",
            model=trafo.get_default(attr="model", platform=Platform.PYPSA),
            x=trafo.x1pu,
            r=trafo.r1pu,
            g=trafo.gm_pu,  # ignores other shunt loses besides magnitizing looses
            b=trafo.bm_pu,  # ignores other shunt effects besides magnitizing effects
            s_nom=trafo.rating,
            s_max_pu=(
                (trafo.rating / trafo.rating_short_term)
                if not trafo.rating_short_term is None
                else None
            ),  # not exactly equal in meaning, could also be rating_emergency
            num_parallel=1,
            tap_ratio=trafo.tap_ratio,
            tap_position=trafo.tap_initial,
            phase_shift=trafo.phase_shift,
            v_ang_min=trafo.angle_min,
            v_ang_max=trafo.angle_max,
        )
        creation_result = trafo_name[0] in self.pypsa_model.components.transformers.static.index
        if not creation_result:
            Logger.log_to_selected(
                f"Creation in PyPSA failed for TwoWindingTransformer {trafo.uid}"
            )
        return creation_result

    def add_shunt_from_gdf(self, shunt: Shunt) -> bool:
        """Method for converting GDF Shunt components to PyPSA shunts

        :param shunt: GDF Shunt component to convert
        :type shunt: Shunt
        :return: True if successful else False
        :rtype: bool
        """
        shunt_bus = get_connected_bus(self.core_model.graph, shunt, max_depth=1)
        # If no load bus was found the function fails
        if shunt_bus is None:
            Logger.log_to_selected(
                f"Conversion of shunt (uid {shunt.uid}) failed because bus was not found"
            )
            return False

        shunt_name = self.pypsa_model.components.shunt_impedances.add(
            name=shunt.uid,
            bus=shunt_bus.uid,
            g=shunt.p / (shunt_bus.nominal_voltage**2),
            b=shunt.q / (shunt_bus.nominal_voltage**2),
        )

        creation_result = shunt_name[0] in self.pypsa_model.components.shunt_impedances.static.index
        if not creation_result:
            Logger.log_to_selected(f"Creation in PyPSA failed for Shunt {shunt.uid}")
        return creation_result

    def add_generator_impedance_from_gdf_voltage_source(
        self, voltage_source: VoltageSource
    ) -> bool:
        """Method for converting GDF VoltageSource to combination of generator and impedance
        in PyPSA.

        :param voltage_source: GDF VoltageSource to convert
        :type voltage_source: VoltageSource
        :return: True if successful else False
        :rtype: bool
        """
        voltage_source_bus = get_connected_bus(self.core_model.graph, voltage_source, max_depth=1)

        z_base = get_z_base(voltage_source, self.core_model)

        if voltage_source_bus is None:
            Logger.log_to_selected(
                f"Conversion of voltage source (uid {voltage_source.uid}) failed"
                + " because bus was not found"
            )
            return False

        new_line_uid = self.core_model.get_valid_id()
        new_bus_uid = self.core_model.get_valid_id()

        bus_name = self.pypsa_model.components.buses.add(
            name=new_bus_uid,
            v_nom=voltage_source.u_setp * voltage_source_bus.nominal_voltage,
            carrier="AC",
        )

        voltage_source_name = self.pypsa_model.components.generators.add(
            name=voltage_source.uid,
            bus=new_bus_uid,
            control="Slack",  # could also be PV
            # p_nom # defualts to 0, but maybe should be high
            # so the generator actually holds the network voltage?
        )

        line_name = self.pypsa_model.components.lines.add(
            name=new_line_uid,
            bus0=new_bus_uid,
            bus1=voltage_source_bus,
            r=voltage_source.r_pu * z_base,
            x=voltage_source.x_pu * z_base,
            # s_nom   # should maybe also be limited
        )

        if not (
            line_name[0] in self.pypsa_model.components.lines.index
            and bus_name[0] in self.pypsa_model.components.buses.index
            and voltage_source_name[0] in self.pypsa_model.components.generators.index
        ):
            Logger.log_to_selected(
                f"Conversion of VoltageSource {voltage_source.uid} failed because at "
                + "least one substitution component was not found after creation"
            )
            return False

        Logger.log_to_selected(
            "[EXPERIMENTAL]: Conversion from voltage source to Slack Generator"
            + "with line impedance and bus took place \n"
            + f"The generator received the uid {voltage_source.uid} of the voltage source"
            + f" and the bus and line the new uids {new_bus_uid} and {new_line_uid} respectively"
        )

        return True
