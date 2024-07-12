from epowcore.gdf.bus import Bus
from epowcore.gdf.component import Component
from epowcore.gdf.data_structure import DataStructure
from epowcore.generic.component_graph import ComponentGraph
from epowcore.jmdl.to_gdf.components.line import EPowLine
from epowcore.gdf.external_grid import ExternalGrid
from epowcore.gdf.generators.generator import Generator
from epowcore.gdf.load import Load
from epowcore.gdf.port import Port
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.subsystem import Subsystem
from epowcore.gdf.switch import Switch
from epowcore.gdf.tline import TLine
from epowcore.generic.logger import Logger
from epowcore.jmdl.to_gdf.components.transformer import EPowTransformer


def post_import(data_structure: DataStructure) -> None:
    # rename "normal" connectors
    rename_connectors(data_structure.graph)
    # rename port connectors
    for component in data_structure.graph.nodes:
        if isinstance(component, Port):
            Logger.log_to_selected(
                f"Port outside of subsystem. Not sure what to do: {component.name} ({component.uid})"
            )
        elif isinstance(component, Subsystem):
            rename_port_connectors(data_structure, component, data_structure.graph)
    # aggregate port components
    for component in data_structure.graph.nodes:
        if isinstance(component, Subsystem):
            aggregate_ports(component)

    # at this point, the DataStructure should be a valid model
    convert_transmission_lines(data_structure)
    convert_transformers(data_structure)


def convert_transmission_lines(data_structure: DataStructure) -> None:
    epowlines = _get_epow_lines(data_structure.graph)
    for line in epowlines:
        line.replace_with_tline(data_structure)


def _get_epow_lines(graph: ComponentGraph) -> list[EPowLine]:
    lines = []
    for c in graph.nodes:
        if isinstance(c, EPowLine):
            lines.append(c)
        elif isinstance(c, Subsystem):
            lines.extend(_get_epow_lines(c.graph))
    return lines

def convert_transformers(data_structure: DataStructure) -> None:
    epowtrafos = _get_epow_transformers(data_structure.graph)
    for trafo in epowtrafos:
        trafo.replace_with_trafo(data_structure)


def _get_epow_transformers(graph: ComponentGraph) -> list[EPowTransformer]:
    trafos = []
    for c in graph.nodes:
        if isinstance(c, EPowTransformer):
            trafos.append(c)
        elif isinstance(c, Subsystem):
            trafos.extend(_get_epow_transformers(c.graph))
    return trafos

def aggregate_ports(subsystem: Subsystem) -> None:
    ports: dict[int, list[Port]] = {}
    for component in subsystem.graph.nodes:
        if isinstance(component, Port):
            if not component.connection_component in ports:
                ports[component.connection_component] = [component]
            else:
                ports[component.connection_component].append(component)
    for port_list in ports.values():
        if len(port_list) < 2:
            continue
        base_port = port_list[0]
        for port in port_list[1:]:
            for node1, node2, data in subsystem.graph.edges.data(port):
                node = node1 if node1 != port else node2
                subsystem.graph.add_edge(base_port, node)
                new_data = {
                    base_port.uid: data[port.uid],
                    node.uid: data[node.uid],
                }
                subsystem.graph.edges.update(base_port, node, new_data)
                subsystem.graph.remove_node(port)


def rename_port_connectors(
    data_structure: DataStructure,
    subsystem: Subsystem,
    external_graph: ComponentGraph,
) -> None:
    for component in subsystem.graph.nodes:
        if isinstance(component, Port):
            conn_comp = data_structure.get_component_by_id(component.connection_component)[0]
            if conn_comp is None:
                Logger.log_to_selected(f"Connected component not found: ID = {component.uid}")
                continue
            external_edge_data = None
            for edge in external_graph.edges.data(conn_comp):
                if subsystem in edge:
                    external_edge_data = edge[2]
                    break
            if external_edge_data is None:
                Logger.log_to_selected("No edge found between connected component and subsystem.")
                continue
            # we use a copy of the list to avoid potentially introduced name collisions
            ext_subsys_conns = list(external_edge_data[subsystem.uid])
            ext_comp_conns = list(external_edge_data[conn_comp.uid])

            for node1, node2, data in subsystem.graph.edges.data(component):
                node = node1 if node1 != component else node2
                internal_port_conns = data[component.uid]
                internal_node_conns = data[node.uid]

                # In the cross-subsystem connection, the subsystem takes the place of its internal
                # component. The port takes the place of the external component. Thus, these two
                # surrogates also have the same connector names as the original components.
                for iport, inode in zip(internal_port_conns, internal_node_conns):
                    for ext_subsys_conn, ext_node_conn in zip(ext_subsys_conns, ext_comp_conns):
                        if iport == ext_subsys_conn:
                            _replace_connector_pairs(component.uid, data, [(iport, ext_node_conn)])
                            _replace_connector_pairs(
                                subsystem.uid, external_edge_data, [(iport, inode)]
                            )

        elif isinstance(component, Subsystem):
            rename_port_connectors(data_structure, component, subsystem.graph)


def rename_connectors(graph: ComponentGraph) -> None:
    """Rename the connectors of an imported model to conform with GDF standards.

    :param graph: The graph of the imported model.
    :type graph: ComponentGraph
    """
    for comp1, comp2, data in graph.edges.data():
        _rename_connectors_inner(comp1, data)
        _rename_connectors_inner(comp2, data)
    for component in graph.nodes:
        if isinstance(component, EPowTransformer):
            neighbors: list[Bus] = list(graph.neighbors(component))  # type: ignore
            if len(neighbors) == 0:
                continue
            if any(not isinstance(n, Bus) for n in neighbors):
                Logger.log_to_selected(
                    f"Transformer not connected to buses: {component.name} ({component.uid})"
                )
                continue
            if len(neighbors) == 1:
                _, _, data = list(graph.edges.data(component))[0]
                # No way to know this -> use HV for consistency
                data[component.uid] = ["HV"]
                continue
            hv, lv = None, None
            if neighbors[0].nominal_voltage >= neighbors[1].nominal_voltage:
                hv = neighbors[0]
                lv = neighbors[1]
            else:
                hv = neighbors[1]
                lv = neighbors[0]
            for comp1, comp2, data in graph.edges.data(component):
                if hv.uid in data:
                    data[component.uid] = ["HV"]
                elif lv.uid in data:
                    data[component.uid] = ["LV"]


def _rename_connectors_inner(component: Component, data: dict[int, list[str]]) -> None:
    if isinstance(component, (TLine, EPowLine, Switch)):
        _replace_connector_pairs(component.uid, data, [("to", "A"), ("from", "B")])
    elif isinstance(component, (Bus, ExternalGrid, Load, Shunt, Generator)):
        connectors = data[component.uid]
        # These components only have one connector -> use default value
        data[component.uid] = ["" for _ in connectors]
    elif isinstance(component, Subsystem):
        rename_connectors(component.graph)


def _replace_connector_pairs(
    uid: int, edge_data: dict[int, list[str]], replacements: list[tuple[str, str]]
) -> None:
    connectors = edge_data[uid]

    for old, new in replacements:
        connectors = [new if x == old else x for x in connectors]

    edge_data[uid] = connectors
