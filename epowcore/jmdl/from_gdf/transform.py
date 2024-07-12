import copy

from epowcore.gdf import DataStructure
from epowcore.gdf.bus import Bus
from epowcore.gdf.extended_ward import ExtendedWard
from epowcore.gdf.external_grid import ExternalGrid
from epowcore.gdf.generators.generator import Generator
from epowcore.gdf.impedance import Impedance
from epowcore.gdf.load import Load
from epowcore.gdf.port import Port
from epowcore.gdf.pv_system import PVSystem
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.subsystem import Subsystem
from epowcore.gdf.switch import Switch
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.voltage_source import VoltageSource
from epowcore.gdf.ward import Ward
from epowcore.generic.component_graph import ComponentGraph
from epowcore.generic.constants import Platform
from epowcore.generic.logger import Logger
from epowcore.generic.manipulation.merge_components import merge_components
from epowcore.generic.manipulation.insert_buses import insert_buses

WHITE_LIST = (
    Bus,
    ExternalGrid,
    Generator,
    TLine,
    PVSystem,
    Load,
    Shunt,
    Switch,
    TwoWindingTransformer,
    VoltageSource,
    Subsystem,
    Port,
)


def transform(data_structure: DataStructure) -> DataStructure:
    """Transform the generic model to make it compatible to JMDL."""
    data_struct = copy.deepcopy(data_structure)

    nodes = list(data_struct.graph.nodes)
    for n in nodes:
        # remove buses without type -> isolated
        if isinstance(n, Bus) and n.lf_bus_type is None:
            Logger.log_to_selected(f"Removing bus without type: {n.name}")
            data_struct.graph.remove_node(n)

    nodes = list(data_struct.graph.nodes)
    for n in nodes:
        # remove nodes without neighbors
        if len(list(data_struct.graph.neighbors(n))) == 0:
            Logger.log_to_selected(f"Removing outlier node: {n.name}")
            data_struct.graph.remove_node(n)

    # Replace extended Ward equivalents with loads, shunts, impedances and voltage sources
    ext_wards = [n for n in data_struct.graph.nodes if isinstance(n, ExtendedWard)]
    for ext_ward in ext_wards:
        ext_ward.replace_with_load_shunt_vsource(data_struct)

    # Replace Ward equivalents with loads and shunts
    # Order is important because ExtendedWard is also a Ward!
    wards = [n for n in data_struct.graph.nodes if isinstance(n, Ward)]
    for ward in wards:
        ward.replace_with_load_and_shunt(data_struct)

    # Replace impedances with lines
    impedances = [n for n in data_struct.graph.nodes if isinstance(n, Impedance)]
    for impedance in impedances:
        impedance.replace_with_line(data_struct, Platform.JMDL)

    three_winding_transformers = data_struct.type_list(ThreeWindingTransformer)

    for three_winding_transformer in three_winding_transformers:
        Logger.log_to_selected(
            f"Replacing three-winding transformer: {three_winding_transformer.name}"
        )
        three_winding_transformer.replace_with_two_winding_transformers(data_struct)

    # Aggregate loads and shunts
    buses = [n for n in data_struct.graph.nodes if isinstance(n, Bus)]
    for bus in buses:
        _aggregate_loads(bus, data_struct)
        _aggregate_shunts(bus, data_struct)

    # Merge neighbouring buses
    for bus in data_struct.type_list(Bus):
        if data_struct.graph.has_node(bus):
            for neighbour in list(data_struct.graph.neighbors(bus)):
                if isinstance(neighbour, Bus):
                    merge_components(data_struct, bus, neighbour)

    _remove_not_supported(data_struct.graph)

    # bus_dict : dict[tuple[str,str], int] = {} # Maps component id and port name to bus id
    insert_buses(data_struct)

    for node in data_struct.graph.nodes:
        if isinstance(node, Subsystem):
            _deaggregate_ports(data_struct, node)

    return data_struct


def _deaggregate_ports(data_structure: DataStructure, subsystem: Subsystem) -> None:
    for component in list(subsystem.graph.nodes):
        if isinstance(component, Port):
            if len(list(subsystem.graph.edges(component))) < 2:
                continue
            count = 1
            for node1, node2, data in subsystem.graph.edges.data(component):
                node = node1 if node1 != component else node2
                new_port = Port(
                    data_structure.get_valid_id(),
                    f"{component.name}_{count}",
                    connection_component=component.connection_component
                )
                subsystem.graph.add_node(new_port)
                subsystem.graph.add_edge(new_port, node)
                new_data = {
                    new_port.uid: data[component.uid],
                    node.uid: data[node.uid],
                }
                subsystem.graph.edges.update(new_port, node, new_data)
                count += 1
            subsystem.graph.remove_node(component)
        elif isinstance(component, Subsystem):
            _deaggregate_ports(data_structure, component)


def _aggregate_loads(bus: Bus, data_structure: DataStructure) -> None:
    loads: list[Load] = [
        n for n in data_structure.graph.neighbors(bus) if isinstance(n, Load)
    ]
    if len(loads) < 2:
        return
    aggregate = Load(
        uid=min(l.uid for l in loads),
        name=f"Agg-Load-{bus.name}",
        coords=bus.coords,
        active_power=sum(l.active_power for l in loads),
        reactive_power=sum(l.reactive_power for l in loads),
    )
    data_structure.graph.remove_nodes_from(loads)
    data_structure.graph.add_edge(bus, aggregate)


def _aggregate_shunts(bus: Bus, data_structure: DataStructure) -> None:
    shunts: list[Shunt] = [
        n for n in data_structure.graph.neighbors(bus) if isinstance(n, Shunt)
    ]
    if len(shunts) < 2:
        return
    aggregate = Shunt(
        uid=min(s.uid for s in shunts),
        name=f"Agg-Shunt-{bus.name}",
        coords=bus.coords,
        q=sum(s.q for s in shunts),
        p=sum(s.p for s in shunts),
    )
    data_structure.graph.remove_nodes_from(shunts)
    data_structure.graph.add_edge(bus, aggregate)


def _remove_not_supported(graph: ComponentGraph) -> None:
    """Remove all nodes that are not supported by JMDL.

    :param graph: The graph to remove the unsupported nodes from.
    :type graph: ComponentGraph
    """
    components = list(graph.nodes)
    for c in components:
        if not isinstance(c, WHITE_LIST):
            Logger.log_to_selected(f"Removing unsupported node: {c.name}")
            graph.remove_node(c)
        elif isinstance(c, Subsystem):
            _remove_not_supported(c.graph)
            # If only ports are left in the Subsystem, remove
            if len(c.graph.nodes) == len(
                [n for n in c.graph.nodes if isinstance(n, Port)]
            ):
                Logger.log_to_selected(f"Removing empty subsystem: {c.name}")
                graph.remove_node(c)
