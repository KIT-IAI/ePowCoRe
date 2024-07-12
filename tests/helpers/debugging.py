from typing import Any
import matplotlib.pyplot as plt
import networkx as nx


def get_neighborhood(graph: nx.Graph, node: Any, depth: int = 2) -> nx.Graph:
    neighborhood = nx.Graph()
    if node in graph.nodes:
        neighborhood.add_node(node)
    for i, j in nx.bfs_edges(graph, node, depth_limit=depth):
        neighborhood.add_edge(i, j)
    return neighborhood


def visualize_graph(graph: nx.Graph, rel_pos: tuple[int, int] = (0, 0), draw: bool = True) -> None:
    """
    Visualize a graph using matplotlib.
    :param graph: The graph to visualize.
    :param rel_pos: The relative position of the graph to the origin.
    """
    pos = {}
    for k, v in nx.kamada_kawai_layout(graph).items():
        pos[k] = (v[0] + rel_pos[0], v[1] + rel_pos[1])

    nx.draw(
        graph,
        labels={n: f"{type(n).__name__} ({n.uid}): {n.name}" for n in graph},
        pos=pos,
    )
    if draw:
        plt.show()
