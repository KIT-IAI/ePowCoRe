from collections import defaultdict
import math

import networkx as nx
from pyapi_rts.api import Draft, Subsystem
from pyapi_rts.api.lark.rlc_tline import RLCTLine

from pyapi_rts.api.component import Component as RSCADComponent
from epowcore.gdf.component import Component
from epowcore.generic.component_graph import ComponentGraph


class GraphTransformerRscad:
    """GraphTransformer class for RSCAD"""

    def __init__(self) -> None:
        super().__init__()
        # Setup dictionary containing the load unit costs of hierarchy boxes
        # TODO: What are default costs?
        self.load_unit_costs: dict[str, int] = defaultdict(lambda: 10)
        self.line_connection_graph: dict = defaultdict(list)

    def relabel_nodes(
        self, graph: ComponentGraph, transformation_dict: dict[Component, str]
    ) -> nx.Graph:
        """Relabels the nodes of the given graph with the given transformation_dict."""
        int_graph = graph.get_internal_graph()
        # edge = tuple: component uid, component uid, data
        for left, right, data in list(graph.edges.data()):
            left_id = transformation_dict[left]
            right_id = transformation_dict[right]
            left_data = data.get(left.uid, [])
            right_data = data.get(right.uid, [])
            int_graph.edges[left, right].update({left_id: left_data, right_id: right_data})
        return nx.relabel_nodes(int_graph, transformation_dict)

    def get_subgraph(self, nodes: list[RSCADComponent], graph: nx.Graph) -> nx.Graph:
        """Returns a copy of a subgraph from the given nodes of graph"""
        return graph.subgraph([node.uuid for node in nodes]).copy()

    def replace_subgraph(
        self,
        graph: nx.Graph,
        subgraph: nx.Graph,
        new_node: RSCADComponent,
        draft: Draft,
        bus_edge: RSCADComponent | None = None,
    ) -> list[RSCADComponent]:
        """Replaces the given subgraph with newNode in graph.
        newNode gets the outgoing edges from subgraph to graph.
        Returns a list of nodes to remove from the original graph"""
        # Get all edges between subgraph and graph

        outgoing_edges = [
            e
            for e in graph.edges
            if (e[0] in subgraph and e[1] in graph and e[1] not in subgraph)
            or (e[0] in graph and e[1] in subgraph and e[0] not in subgraph)
        ]

        # Remove all edges of the subgraph from the original graph, except for RSCAD busLabel
        nodes_to_remove = []
        for node in subgraph.nodes:
            node_by_id = draft.get_by_id(node)
            if node_by_id is not None and node_by_id.type != "rtds_sharc_sld_BUSLABEL":
                graph.remove_node(node)
                nodes_to_remove.append(node)
        # Add new node to the graph
        graph.add_node(new_node.uuid)
        # Replace old node of the edges with the new node
        outgoing_temp = [
            (new_node.uuid, j) if i in nodes_to_remove else (i, j) for (i, j) in outgoing_edges
        ]
        outgoing_changed = [
            (i, new_node.uuid) if j in nodes_to_remove else (i, j) for (i, j) in outgoing_temp
        ]
        graph.add_edges_from(outgoing_changed)
        if bus_edge is not None:
            graph.add_edge(bus_edge.uuid, new_node.uuid)
        return nodes_to_remove

    def replace_single_subgraph(
        self, graph: nx.Graph, subgraph: nx.Graph, new_node: RSCADComponent
    ) -> list[RSCADComponent]:
        """Replaces a group of nodes with a single new node without adding any edges from the removed nodes back"""
        nodes_to_remove = []
        for node in subgraph.nodes:
            graph.remove_node(node)
            nodes_to_remove.append(node)
        # Add new node to the graph
        graph.add_node(new_node.uuid)
        return nodes_to_remove

    def create_tline_connection_graph(
        self, subsystem: Subsystem, tli_files: list[RLCTLine]
    ) -> nx.Graph:
        """Creates a connection graph on the highest hierarchy level containing the hierarchy
        bus boxes as nodes and TLine elements as edges"""
        connection_graph = nx.Graph()
        # Construct the nodes and add their weight as an attribute
        hierarchy_ids = [c.uuid for c in subsystem.get_components(False, False) if c.type == "HIERARCHY"]
        connection_graph.add_nodes_from(hierarchy_ids, visited=False)
        edge_nodes = self.extract_edges()
        nx.set_node_attributes(connection_graph, self.load_unit_costs, "LoadUnitCosts")
        for hierarchy in hierarchy_ids:
            edges = self.line_connection_graph.get(hierarchy)
            if edges is not None:
                for edge in edges:
                    nodes = edge_nodes[edge]
                    tli_file = edge
                    # Add the transmission time of the TLine as an edge attribute
                    propagation_time = self.get_transmission_time(tli_file, tli_files)
                    connection_graph.add_edge(nodes[0], nodes[1], time=propagation_time)
        return connection_graph

    def get_transmission_time(self, tline: RLCTLine, tli_files: list[RLCTLine]) -> float:
        """Returns the lowest transmission time of the given RLCTLine file"""
        time = 0.00005
        for tli_file in tli_files:
            if tli_file.name == tline:
                l0 = tli_file.xind0 / (2 * math.pi * tli_file.frequency)
                if tli_file.xcap0 != 0:
                    c0 = 1 / (2 * math.pi * tli_file.frequency * tli_file.xcap0)
                else:
                    c0 = 1
                time0 = math.sqrt(l0 * c0) * tli_file.length
                l1 = tli_file.xind1 / (2 * math.pi * tli_file.frequency)
                if tli_file.xcap0 != 0:
                    c1 = 1 / (2 * math.pi * tli_file.frequency * tli_file.xcap1)
                else:
                    c1 = 1
                time1 = math.sqrt(l1 * c1) * tli_file.length
                # Return the minimum of the transmission times
                return min(time0, time1)
        return time

    def distribute_load_unit_costs(
        self,
        load_costs: int,
        subsystem: Subsystem,
        propagation_time: float,
        max_load: int,
        tli_files: list[RLCTLine],
    ) -> set[str]:
        """Returns nodes to move into a new subsystem to reduce the load unit costs of the given subsystem

        :param load_costs: The load unit costs of the subsystem
        :param subsystem: The subsystem to distribute the load unit costs in
        :param propagation_time: The maximum propagation time of the subsystem
        :param max_load: The maximum load unit costs of the subsystem
        :param tli_files: The TLines between the hierarchy bus boxes
        :return: The nodes to move into a new subsystem
        """
        hierarchy_graph = self.create_tline_connection_graph(subsystem, tli_files)
        # TODO: Causes a key error when the case is divided into a third subsystem
        # Some nodes are in the graph without load unit costs
        # and some nodes in the graph are not in the subsystem
        moved_nodes = set()
        edges_to_remove = {
            (u, v) for u, v, d in hierarchy_graph.edges(data=True) if d["time"] >= propagation_time
        }
        subgraph_dict = {}
        # Check the every node for its neighbors
        # Remove the edges
        hierarchy_graph.remove_edges_from(edges_to_remove)
        # Write all subgraphs with their costs into a dictionary

        for subgraph in (
            hierarchy_graph.subgraph(c) for c in nx.connected_components(hierarchy_graph)
        ):
            sum_cost = sum(subgraph.nodes[node]["LoadUnitCosts"] for node in subgraph.nodes)
            subgraph_dict[subgraph] = sum_cost

        # Move until the load costs are below the maximum load
        for subgraph, cost in subgraph_dict.items():
            if load_costs < max_load:
                break
            load_costs -= cost
            moved_nodes.update(subgraph.nodes)
        return moved_nodes

    def extract_edges(self) -> dict[RSCADComponent, list]:
        """Return a dict containing the Tlines as keys with their connected hierarchies as values"""
        connections = list(self.line_connection_graph.items())
        edge_dictionary = defaultdict(list)
        for connection in connections:
            for edge in connection[1]:
                # Name of the Tline as key to merge the sending and receiving components as one key
                edge_dictionary[edge].append(connection[0])
        return edge_dictionary
