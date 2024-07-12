from typing import Mapping
import matplotlib.pyplot as plt
import networkx as nx


def visualize_graph(
    graph: nx.Graph,
    show_labels: bool = False,
    file_name: str | None = None,
    layout: dict | None = None,
    width: int = 10,
    height: int = 10,
    seed: int | None = None,
) -> Mapping:
    """Visualize network graph."""

    pos = (
        nx.spring_layout(graph, seed=seed)
        if layout is None
        else nx.spring_layout(graph, pos=layout, fixed=list(layout.keys()), seed=seed)
    )

    plt.figure(figsize=(width, height))
    nx.draw_networkx_nodes(
        graph,
        pos=pos,
    )
    nx.draw_networkx_edges(
        graph,
        pos=pos,
    )
    if show_labels:
        labels = {n: f"{type(n).__name__} ({n.uid}): {n.name}" for n in graph}
        nx.draw_networkx_labels(graph, pos, labels=labels)

    plt.tight_layout()
    if file_name is not None:
        plt.savefig(file_name)
        plt.close()
    else:
        plt.show()
    return pos


def color_voltage(voltage: int) -> str:
    """
    Return color for voltage.
    :param voltage: Voltage.
    :return: Color hexstring.
    """
    return {
        500: "#f068f9",
        380: "#d80000",
        345: "#220afc",
        300: "#0afce0",
        230: "#8e1818",
        220: "#1ed30a",
        138: "#bc0d0d",
        30: "#0a72d3",
        25: "#16f20e",
        20: "#f20ee3",
        16.5: "#fc0004",
        12.5: "#918f08",
    }.get(voltage, "yellow")
