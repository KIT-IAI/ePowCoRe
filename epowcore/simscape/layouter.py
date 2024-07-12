from math import sqrt
import matlab.engine

import networkx as nx

from epowcore.gdf.component import Component
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.tools import set_position


def layout_model(
    eng: matlab.engine.MatlabEngine,
    graph: nx.Graph,
    created_components: dict[Component, SimscapeBlock],
) -> None:
    """Calculate a layout for the given [graph] and place the [created_components] on the canvas
    accordingly.

    :param eng: The Matlab engine.
    :type eng: matlab.engine
    :param graph: The graph describing the system.
    :type graph: nx.Graph
    :param created_components: Dictionary mapping the graph components to created Simscape blocks.
    :type created_components: dict[Component, SimscapeBlock]
    """
    # estimate the required size of the canvas
    # assumption: each component needs around 400 x 400 units; rounded to 100s
    width = round(sqrt(2 * len(graph.nodes)) * 4) * 100
    height = width / 2

    # let networkx create a layout for the graph
    # spectral_layout is also promising
    pos_dict = nx.kamada_kawai_layout(graph)

    x_coords: list[float] = [c[0] for c in pos_dict.values()]
    y_coords: list[float] = [c[1] for c in pos_dict.values()]

    min_x = min(x_coords)
    max_x = max(x_coords)
    min_y = min(y_coords)
    max_y = max(y_coords)
    width_orig = max_x - min_x if max_x > min_x else 1
    height_orig = max_y - min_y if max_y > min_y else 1

    # rescale coordinates
    x_coords = [(x - min_x) * width / width_orig for x in x_coords]
    y_coords = [(y - min_y) * height / height_orig for y in y_coords]
    # place coordinates on coarse grid to achieve more straight lines
    x_coords = [round(x / 50) * 50 for x in x_coords]
    y_coords = [round(y / 100) * 100 for y in y_coords]

    new_pos_dict = {}
    for component, x, y in zip(pos_dict, x_coords, y_coords):
        new_pos_dict[component] = (x, y)

    for component, block in created_components.items():
        if component not in new_pos_dict:
            continue
        pos_x, pos_y = new_pos_dict[component]
        set_position(eng, block, pos_x, pos_y)
