import math
import networkx as nx
from pyapi_rts.api import Component, Hierarchy


from pyapi_rts.generated.enums.DescornameEnumParameter import DescornameEnum
from pyapi_rts.generated.rtdsIEEET1def import rtdsIEEET1def
from pyapi_rts.generated.rtdsIEEEG1def import rtdsIEEEG1def
from epowcore.generic.configuration import Configuration

from epowcore.generic.logger import Logger

from epowcore.rscad.graph_transformer_rscad import GraphTransformerRscad

SCALE_HIERARCHIES_TO = Configuration().get("RSCAD.HierarchySize")


def round_to_multiple(val: int, base: int) -> int:
    """Modifies the value x so it is placed correctly on the Rscad grid"""
    return base * math.floor(val / base)


def create_hierarchy(name: str, xsize: int = 112, ysize: int = 112) -> Hierarchy:
    """Create a hierarchybox with the given options"""
    hierarchy = Hierarchy()
    hierarchy.BoxParameters.Name.value = name
    hierarchy.BoxParameters.DESC_OR_NAME.value = DescornameEnum.Name
    hierarchy.x = xsize
    hierarchy.y = ysize
    return hierarchy


def get_all_subgraphs(graph: nx.Graph) -> list[nx.Graph]:
    """Returns copies of all subgraphs in the given graph"""
    return [graph.subgraph(c).copy() for c in nx.connected_components(graph)]


def get_connections_dict(
    components: list[Component], subgraph: nx.Graph
) -> dict[str, list[tuple[Component, list[str]]]]:
    """Create a dictionary of all connections of the given components, returning a mapping
    of the component id to a list of connected components and the names of the connection ports

    :param components: List of components to get the connections from
    :param subgraph: Graph to get the connections from
    :return: Dictionary of all connections of the given components in the format {component_id: [(connected_component, connection_names), ...]}
    """
    connections_dict: dict[str, list[tuple[Component, list[str]]]] = {}
    for component in components:
        for u, v, data in subgraph.edges(component.uuid, data=True):
            # connection is in format (component_id_1, component_id_2, {connection_name: connection_value, ...})
            if u not in data:
                data[u] = [""]  # Set default value
            if v not in data:
                data[v] = [""]
            if u not in connections_dict:
                connections_dict[u] = [(component, data[u])]
            else:
                connections_dict[u].append((component, data[u]))
            if v not in connections_dict:
                connections_dict[v] = [(component, data[v])]
            else:
                connections_dict[v].append((component, data[v]))
    return connections_dict


def check_generator_connections(
    generator: Component, components: list[Component]
) -> list[Component]:
    """
    Check if the given generator has all necessary control elements for its ingoing signals
    and adds them if necessary.
    """
    # TODO: Check is specific for the generator type for more added generator types this has be also edited
    component_type_list = [component.type for component in components]
    frequency = generator.GENERALMODELCONFIGURATION.HTZ.value  # type: ignore
    generator_name = generator.name
    log_string = f"HIERARCHY|{generator_name}|Additional: "
    if generator.type == "lf_rtds_sharc_sld_MACV31":
        if "_rtds_IEEEG1.def" not in component_type_list:
            rscad_governor = rtdsIEEEG1def()
            rscad_governor.CONFIGURATION.HTZ.value = frequency
            rscad_governor.CONFIGURATION.Ghp.value = generator_name
            components += [rscad_governor]
            log_string += f"{rscad_governor.type}, "
        if "_rtds_IEEET1.def" not in component_type_list:
            rscad_exciter = rtdsIEEET1def()
            rscad_exciter.CONFIGURATION.HTZ.value = frequency
            rscad_exciter.CONFIGURATION.Gen.value = generator_name
            components += [rscad_exciter]
            log_string += f"{rscad_exciter.type}"
        # Only print out the logString if something was changed
        if log_string != f"HIERARCHY|{generator_name}|Additional: ":
            Logger.log_to_selected(log_string)
    return components


def add_elements_to_hierarchy(
    hierarchy: Hierarchy,
    components: list[Component],
    gm: GraphTransformerRscad,
    bus_label_duplicate: Component | None = None,
    connecting_items: list[Component] | None = None,
) -> None:
    """Adds the components to to the given hierarchy and adds the duplicated busLabel.
    The busLabel has to be directly added as the component because adding it over the uuid
    would add the original busLabel instead."""
    load_cost = 0
    for component in components:
        if component.type == "HIERARCHY":
            load_cost += gm.load_unit_costs[component.uuid]
            del gm.load_unit_costs[component.uuid]
        else:
            load_cost += component.load_units
        hierarchy.add_component(component)
    if bus_label_duplicate is not None:
        hierarchy.add_component(bus_label_duplicate)
        load_cost += bus_label_duplicate.load_units
    # Add components like busline or wire to the hierarchy
    if connecting_items is not None:
        for item in connecting_items:
            hierarchy.add_component(item)
    gm.load_unit_costs[hierarchy.uuid] = load_cost
    Logger.log_to_selected(
        f"Added {len(components)} components to hierarchy {hierarchy.BoxParameters.Name}"
    )
    update_hierarchy_size(hierarchy)


def update_hierarchy_size(hierarchy: Hierarchy) -> None:
    """
    Scales the size of the hierarchy canvas and zooms out if the hierarchy is too big.
    """
    max_x = 0
    max_y = 0
    for component in hierarchy.get_components():
        max_x = max(max_x, component.x + component.width + 25)
        max_y = max(max_y, component.y + component.height + 25)
    if max_x > SCALE_HIERARCHIES_TO[0] or max_y > SCALE_HIERARCHIES_TO[1]:
        scale_x = SCALE_HIERARCHIES_TO[0] / max_x
        scale_y = SCALE_HIERARCHIES_TO[1] / max_y
        scale = min(scale_x, scale_y)
        max_x = SCALE_HIERARCHIES_TO[0]
        max_y = SCALE_HIERARCHIES_TO[1]
        hierarchy.set_by_key("zoomFactor", int(scale * 100))
    hierarchy.set_by_key("canvasWidth", max_x)
    hierarchy.set_by_key("canvasHeight", max_y)
