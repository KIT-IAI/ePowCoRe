"""GraphTransformer functions for PowerFactory"""

import networkx as nx
import powerfactory as pf

from epowcore.gdf.component import Component


def create_edges(
    graph: nx.Graph,
    lookup_dict: dict[pf.DataObject, Component],
    edge_dict: dict[pf.DataObject, dict[pf.DataObject, list[str]]],
) -> None:
    """Creates edges for each connection of the PowerFactory node if both nodes are in the graph.

    Example of edge_dict:
    {tline: {
        terminal_a: "A",
        terminal_b: "B"
    }}

    :param graph: The graph to add the edges to.
    :type graph: nx.Graph
    :param lookup_dict: A dictionary containing a mapping from pf.DataObject to Component
    :type lookup_dict: dict
    :param edge_dict: A dictionary of dictionaries containing edge data.
    :type edge_dict: dict
    """
    # Basic idea here: iterate over the terminals and create the connections for each terminal
    # Assumption: other connections (such as generator to governor) are created elsewhere!
    for element in filter(lambda c: c.GetClassName() == "ElmTerm", graph.nodes):
        # Go through each connection the PowerFactory terminal has
        for cub in filter(lambda c: c.GetClassName() == "StaCubic", element.GetContents()):
            connection = cub.obj_id
            # Look if both nodes are keys in the dictionary
            if element in lookup_dict and connection in lookup_dict:
                graph.add_edge(element, connection)
                # Add edge data (connection name) to created edge
                if connection in edge_dict:
                    graph.edges[element, connection].update(
                        {lookup_dict[connection].uid: edge_dict[connection][element]}
                    )

    # for switch in filter(lambda n: n.GetClassName() in ('StaSwitch'), graph.nodes):
    #     graph.add_edge(switch, switch.fold_id.cterm)
    #     graph.add_edge(switch, switch.fold_id.obj_id)
    #     graph.remove_edge(switch.fold_id.cterm, switch.fold_id.obj_id)


def relabel_nodes(graph: nx.Graph, transformation_dict: dict) -> nx.Graph:
    """Relabels the nodes of the given graph with the given transformation_dict."""
    return nx.relabel_nodes(graph, transformation_dict)
