import copy

from epowcore.gdf.bus import Bus
from epowcore.gdf.core_model import CoreModel
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
from epowcore.generic.manipulation.insert_buses import insert_buses
from epowcore.generic.manipulation.merge_components import merge_components

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


def transform(core_model: CoreModel) -> CoreModel:
    """Transform the generic model to make it compatible to JMDL."""
    core_model_tr = copy.deepcopy(core_model)

    nodes = list(core_model_tr.graph.nodes)
    for n in nodes:
        # remove buses without type -> isolated
        if isinstance(n, Bus) and n.lf_bus_type is None:
            Logger.log_to_selected(f"Removing bus without type: {n.name}")
            core_model_tr.graph.remove_node(n)

    nodes = list(core_model_tr.graph.nodes)
    for n in nodes:
        # remove nodes without neighbors
        if len(list(core_model_tr.graph.neighbors(n))) == 0:
            Logger.log_to_selected(f"Removing outlier node: {n.name}")
            core_model_tr.graph.remove_node(n)

    # Replace extended Ward equivalents with loads, shunts, impedances and voltage sources
    ext_wards = [n for n in core_model_tr.graph.nodes if isinstance(n, ExtendedWard)]
    for ext_ward in ext_wards:
        ext_ward.replace_with_load_shunt_vsource(core_model_tr)

    # Replace Ward equivalents with loads and shunts
    # Order is important because ExtendedWard is also a Ward!
    wards = [n for n in core_model_tr.graph.nodes if isinstance(n, Ward)]
    for ward in wards:
        ward.replace_with_load_and_shunt(core_model_tr)

    # Replace impedances with lines
    impedances = [n for n in core_model_tr.graph.nodes if isinstance(n, Impedance)]
    for impedance in impedances:
        impedance.replace_with_line(core_model_tr, Platform.JMDL)

    three_winding_transformers = core_model_tr.type_list(ThreeWindingTransformer)

    for three_winding_transformer in three_winding_transformers:
        Logger.log_to_selected(
            f"Replacing three-winding transformer: {three_winding_transformer.name}"
        )
        three_winding_transformer.replace_with_two_winding_transformers(core_model_tr)

    # Aggregate loads and shunts
    buses = [n for n in core_model_tr.graph.nodes if isinstance(n, Bus)]
    for bus in buses:
        _aggregate_loads(bus, core_model_tr)
        _aggregate_shunts(bus, core_model_tr)

    # Merge neighbouring buses
    for bus in core_model_tr.type_list(Bus):
        if core_model_tr.graph.has_node(bus):
            for neighbour in list(core_model_tr.graph.neighbors(bus)):
                if isinstance(neighbour, Bus):
                    merge_components(core_model_tr, bus, neighbour)

    _remove_not_supported(core_model_tr.graph)

    # bus_dict : dict[tuple[str,str], int] = {} # Maps component id and port name to bus id
    insert_buses(core_model_tr)

    for node in core_model_tr.graph.nodes:
        if isinstance(node, Subsystem):
            _deaggregate_ports(core_model_tr, node)

    return core_model_tr


def _deaggregate_ports(core_model: CoreModel, subsystem: Subsystem) -> None:
    for component in list(subsystem.graph.nodes):
        if isinstance(component, Port):
            if len(list(subsystem.graph.edges(component))) < 2:
                continue
            count = 1
            for node1, node2, data in subsystem.graph.edges.data(component):
                node = node1 if node1 != component else node2
                new_port = Port(
                    core_model.get_valid_id(),
                    f"{component.name}_{count}",
                    connection_component=component.connection_component,
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
            _deaggregate_ports(core_model, component)


def _aggregate_loads(bus: Bus, core_model: CoreModel) -> None:
    loads: list[Load] = [n for n in core_model.graph.neighbors(bus) if isinstance(n, Load)]
    if len(loads) < 2:
        return
    aggregate = Load(
        uid=min(l.uid for l in loads),
        name=f"Agg-Load-{bus.name}",
        coords=bus.coords,
        active_power=sum(l.active_power for l in loads),
        reactive_power=sum(l.reactive_power for l in loads),
    )
    core_model.graph.remove_nodes_from(loads)
    core_model.graph.add_edge(bus, aggregate)


def _aggregate_shunts(bus: Bus, core_model: CoreModel) -> None:
    shunts: list[Shunt] = [n for n in core_model.graph.neighbors(bus) if isinstance(n, Shunt)]
    if len(shunts) < 2:
        return
    aggregate = Shunt(
        uid=min(s.uid for s in shunts),
        name=f"Agg-Shunt-{bus.name}",
        coords=bus.coords,
        q=sum(s.q for s in shunts),
        p=sum(s.p for s in shunts),
    )
    core_model.graph.remove_nodes_from(shunts)
    core_model.graph.add_edge(bus, aggregate)


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
            if len(c.graph.nodes) == len([n for n in c.graph.nodes if isinstance(n, Port)]):
                Logger.log_to_selected(f"Removing empty subsystem: {c.name}")
                graph.remove_node(c)
