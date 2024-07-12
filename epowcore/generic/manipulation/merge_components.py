from epowcore.gdf.bus import Bus
from epowcore.gdf.component import Component
from epowcore.gdf.data_structure import DataStructure
from epowcore.generic.logger import Logger


def merge_components(
    data_struct: DataStructure, component1: Component, component2: Component
) -> bool:
    """
    Tries to merge two components of the same type into one component.
    :param component1: The first component.
    :type component1: Component
    :param component2: The second component.
    :type component2: Component
    :return: True if the components were merged successfully, else False.
    """
    if not isinstance(component1, type(component2)):
        Logger.log_to_selected(
            f"Tried to merge components of different types {type(component1)} and {type(component2)}"
        )
        return False
    if not isinstance(component1, Bus) or not isinstance(component2, Bus):
        Logger.log_to_selected(
            f"Tried to merge components of type {type(component1)} {type(component2)}, should be Bus"
        )
        return False
    if isinstance(component1, Bus) and isinstance(component2, Bus):
        if data_struct.graph.edges[component1, component2] is None:  # type: ignore
            return False
        for edge in data_struct.graph.neighbors(component2):
            edge_data = data_struct.graph.edges[component2, edge]  # type: ignore
            if edge != component1:
                data_struct.graph.add_edge(component1, edge)
                if edge_data is not None:
                    # Set edge data for new connections
                    if component1.uid in edge_data:
                        edge_data[component1.uid] = edge_data[component2.uid]
                        del edge_data[component2.uid]
                    else:
                        edge_data[component1.uid] = [""]
                    data_struct.graph.edges.update(component1, edge, edge_data)
        data_struct.graph.remove_node(component2)
        Logger.log_to_selected(
            f"Merged components {component1.name} and {component2.name}"
        )
        return True
    return False
