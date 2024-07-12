from typing import Any
import copy
from epowcore.gdf import DataStructure
from epowcore.gdf.bus import Bus, BusType
from epowcore.gdf.switch import Switch
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.transformer import Transformer
from epowcore.gdf.impedance import Impedance
from epowcore.generic.component_graph import ComponentGraph
from epowcore.generic.logger import Logger


def remove_internal_nodes(data_structure: DataStructure) -> DataStructure:
    """Remove internal nodes and return a copy of the given data structure.

    This method can lead to a massive reduction in model complexity for models that use
    internal nodes exensively, such as the default busbar systems in PowerFactory.
    Removes internal nodes based on switch positions in the model:
    Switches connecting internal nodes are removed and edges are created
    according to the switch positions. Components connected to isolated internal nodes
    are removed as well.

    :param data_structure: The data structure to remove internal nodes from.
    :type data_structure: DataStructure
    :return: The resulting data structure.
    :rtype: DataStructure
    """
    data_struct = copy.deepcopy(data_structure)

    internal_nodes = _get_internal_nodes(data_struct.graph)

    for inode in internal_nodes:
        _remove_open_switches(inode, data_struct.graph)
        degree = data_struct.graph.degree[inode]
        if degree == 0:
            data_struct.graph.remove_node(inode)
        elif degree == 1:
            neighbor = next(data_struct.graph.neighbors(inode))
            if not isinstance(neighbor, (TLine, Transformer, Impedance)):
                Logger.log_to_selected(f"Removing component {neighbor.name} and {inode.name}")
                data_struct.graph.remove_node(neighbor)
                data_struct.graph.remove_node(inode)
        elif degree == 2:
            neighbors = list(data_struct.graph.neighbors(inode))
            # get one switch neighbor
            i, switch, other_neighbor = None, None, None
            for j, n in enumerate(neighbors):
                if isinstance(n, Switch):
                    i, switch = j, n
                    other_neighbor = neighbors[1 - i]
                    break
            if switch is None or other_neighbor is None:
                raise ValueError("No switch found")
            # get the node on the other side of this switch
            other_node = __get_neighbor_not_component(data_struct, switch, inode)
            # remove the switch
            data_struct.graph.remove_node(switch)
            # create edge between other neighbor and other node
            data_struct.graph.add_edge(other_node, other_neighbor)
            # remove this node
            data_struct.graph.remove_node(inode)

    return data_struct


def __get_neighbor_not_component(
    data_structure: DataStructure, component: Any, not_comp: Any
) -> Any:
    return next(
        filter(
            (lambda n: n != not_comp),
            data_structure.graph.neighbors(component),
        ),
        None,
    )


def _remove_open_switches(inode: Bus, graph: ComponentGraph) -> None:
    neighbors = list(graph.neighbors(inode))
    for neighbor in neighbors:
        if isinstance(neighbor, Switch) and not neighbor.closed:
            graph.remove_node(neighbor)
            Logger.log_to_selected(f"Removing open switch {neighbor.name}")


def _get_internal_nodes(graph: ComponentGraph) -> list:
    return [n for n in graph.nodes if isinstance(n, Bus) and n.bus_type == BusType.INTERNAL]
