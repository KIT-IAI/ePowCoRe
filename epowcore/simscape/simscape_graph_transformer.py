import copy
from typing import Counter
from epowcore.gdf.component import Component
from epowcore.generic.component_graph import ComponentGraph
from epowcore.generic.logger import Logger

from epowcore.simscape.config_manager import ConfigManager
from epowcore.simscape.block import SimscapeBlock


def rename_duplicate_nodes(graph: ComponentGraph) -> ComponentGraph:
    """Find duplicate names and add a number to the end of the name."""
    name_counter: Counter = Counter()
    transformation_dict = {}
    for node in graph.nodes:
        name_counter[node.name] += 1
        if name_counter[node.name] > 1:
            new_node = copy.deepcopy(node)
            new_node.name = node.name + "_" + str(name_counter[node.name])
            transformation_dict[node] = new_node
            Logger.log_to_selected(
                f"Renamed node {node.name} to {new_node.name} due to duplicate name."
            )
        else:
            transformation_dict[node] = node

    return graph.relabel_nodes(transformation_dict)


def add_known_edge_data(
    graph: ComponentGraph,
    created_components: dict[Component, SimscapeBlock],
) -> None:
    """Add edge data depending on the Subsystem template used.

    :param graph: The graph to add the edge data to.
    :param created_components: A dictionary of all gdf components that have a corresponding Simscape block.
    :param created_templates: A dictionary of all gdf subsystem that were created using a template.
    """
    # loop through all components with a template
    for subsystem, template in [
        (key, value.template)
        for key, value in created_components.items()
        if value.template is not None
    ]:
        for neighbor in graph.neighbors(subsystem):
            # get handles of the subsystem's neighbor
            block_n = created_components[neighbor]
            handles_n = ConfigManager.get_all_porthandles(block_n.type)
            if handles_n is None:
                continue

            port_names = []
            for handle in template.port_handles:
                if handle.key in [h.key for h in handles_n]:
                    port_names.append(handle.key)
            if port_names:
                graph.edges.update(
                    subsystem,
                    neighbor,
                    {subsystem.uid: port_names, neighbor.uid: port_names},
                )
