from typing import Any
import networkx as nx
from epowcore.gdf.component import Component

from epowcore.gdf.core_model import CoreModel
from epowcore.generic.tools.visualization import visualize_graph


def get_neighborhood(graph: nx.Graph, node: Any, depth: int = 2) -> nx.Graph:
    neighborhood = nx.Graph()
    if node in graph.nodes:
        neighborhood.add_node(node)
    for i, j in nx.bfs_edges(graph, node, depth_limit=depth):
        neighborhood.add_edge(i, j)
    return neighborhood


def visualize_neighborhood_and_raise_error(
    core_model: CoreModel,
    component: Component,
    error_msg: str = "Could not find port",
) -> None:
    """Visualizes the neighborhood of a component and raises an error."""
    neighborhood = get_neighborhood(core_model.graph.get_internal_graph(), component, depth=3)
    visualize_graph(neighborhood, show_labels=True)
    raise ValueError(error_msg)
