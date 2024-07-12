from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.subsystem import Subsystem


def replace_component(
    core_model: CoreModel, to_replace: Component, replacement: Component
) -> bool:
    """Replaces a component with another component. The connections are transferred.

    :param to_replace: The component to replace.
    :type to_replace: Component
    :param replacement: The replacement component.
    :type replacement: Component
    :return: True if the component was replaced successfully, else False.
    """
    neighbors = list(core_model.graph.neighbors(to_replace))
    edge_data = {}
    connection_ports = []
    for neighbor in neighbors:
        edge_data[neighbor] = core_model.graph.edges[to_replace, neighbor]  # type: ignore
        connection_ports.append(edge_data[neighbor][to_replace.uid])
    # Check if the connections can be transferred
    if not isinstance(replacement, Subsystem) and any(
        map(lambda x: not x in replacement.connector_names, connection_ports)
    ):
        # Some of the connections don't exist in the replacement
        return False

    core_model.graph.remove_node(to_replace)
    replacement.uid = to_replace.uid
    core_model.graph.add_node(replacement)
    for neighbor in neighbors:
        core_model.add_connection(replacement, neighbor)
        if edge_data[neighbor] is not None:
            edge_data[neighbor][replacement.uid] = edge_data[neighbor][to_replace.uid]
            del edge_data[neighbor][to_replace.uid]
            core_model.graph.edges.update(replacement, neighbor, edge_data[neighbor])
    return True
