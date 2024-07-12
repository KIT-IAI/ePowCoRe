from collections.abc import Iterable
import copy as cp
from functools import cached_property
from typing import Iterator

import networkx as nx
from epowcore.gdf.component import Component

from epowcore.generic.component_views import ComponentEdgeView, ComponentNodeView


class ComponentGraph:
    """A typed wrapper around networkx.Graph with a restricted interface."""

    def __init__(self, graph: nx.Graph | None = None) -> None:
        if graph is None:
            self._graph = nx.Graph()
        else:
            self._graph = graph

    def __getitem__(self, node: Component) -> dict[Component, dict[int, list[str]]]:
        return self._graph[node]  # type: ignore

    def __iter__(self) -> Iterator[Component]:
        return iter(self._graph)

    @cached_property
    def nodes(self) -> ComponentNodeView:
        """Return a ComponentNodeView containing the nodes of the graph.
        This implements the most important methods of the classical NodeView,
        but with type restrictions.

        Can be extended, if needed.

        Returns:
            ComponentNodeView: A restricted NodeView containing only elements with type Component.
        """
        return ComponentNodeView(self._graph.nodes)

    @cached_property
    def edges(self) -> ComponentEdgeView:
        """Return a ComponentEdgeView containing the edges of the graph.
        This implements most important EdgeView methods, but with type restrictions.
        Data access methods are cleand up to be clearer and more strictly typed.

        Returns:
            ComponentEdgeView: A restricted EdgeView containing only edges with
            node type Component, and data in form of dict[int, list[str]].
        """
        return ComponentEdgeView(self._graph.edges)

    @property
    def degree(self) -> dict[Component, int]:
        """A DegreeView for the Graph as G.degree or G.degree().

        The node degree is the number of edges adjacent to the node.
        The weighted node degree is the sum of the edge weights for edges incident to that node.
        This object provides an iterator for (node, degree) as well as
        lookup for the degree for a single node.

        Returns:
            dict[Component, int]: The DegreeView of the graph.
        """
        return self._graph.degree  # type: ignore

    def add_node(self, node: Component) -> None:
        # No **attr support: Can not set node attributes while creating.
        # This asserts that only nodes of type Component are added.
        # Could be omitted, if we listen to type warnings.
        assert isinstance(node, Component)
        self._graph.add_node(node)

    def add_nodes_from(self, nodes: Iterator[Component]) -> None:
        # No **attr support: Can not set node attributes while creating.
        for node in nodes:
            self.add_node(node)

    def add_edge(self, u_of_edge: Component, v_of_edge: Component) -> None:
        # No **attr support: Can not set edge attributes while creating.
        assert isinstance(u_of_edge, Component)
        assert isinstance(v_of_edge, Component)
        self._graph.add_edge(u_of_edge, v_of_edge)

    def add_edges_from(self, edges: Iterable[tuple[Component, Component]]) -> None:
        # No **attr support: Can not set edge attributes while creating.
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    def remove_node(self, node: Component) -> None:
        self._graph.remove_node(node)

    def remove_nodes_from(self, nodes: Iterable[Component]) -> None:
        self._graph.remove_nodes_from(nodes)

    def remove_edge(self, u_of_edge: Component, v_of_edge: Component) -> None:
        self._graph.remove_edge(u_of_edge, v_of_edge)

    def neighbors(self, node: Component) -> Iterator[Component]:
        return self._graph.neighbors(node)

    def has_node(self, node: Component) -> bool:
        return self._graph.has_node(node)

    def has_edge(self, u_of_edge: Component, v_of_edge: Component) -> bool:
        return self._graph.has_edge(u_of_edge, v_of_edge)

    def relabel_nodes(self, mapping: dict[Component, Component]) -> "ComponentGraph":
        assert isinstance(mapping, dict)
        nx.relabel_nodes(self._graph, mapping, copy=False)
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ComponentGraph):
            return NotImplemented
        return list(self.nodes) == list(other.nodes) and list(self.edges) == list(other.edges)

    def __hash__(self) -> int:
        return hash(self._graph)

    def to_primitive_dict(self) -> dict:
        """Return the dataclass as a dict containing only primitive data types.

        :return: A dictionary describing the instance with primitive data types only.
        :rtype: dict
        """
        internal_graph = self.get_internal_graph()
        comp_label_dict = {k: k.to_export_str() for k in internal_graph.nodes}
        label_comp_dict = {k.to_export_str(): k.to_primitive_dict() for k in internal_graph.nodes}

        export_graph = nx.relabel_nodes(internal_graph, comp_label_dict)

        return {
            "graph": nx.to_dict_of_dicts(export_graph),
            "components": label_comp_dict,
        }

    def sanity_check(self) -> bool:
        """Check the validity of the graph, meaning the types and uniqueness of the nodes and edges.

        :return: True if the model is valid, else False.
        """
        # Check the types of the components
        node_type_check = all(isinstance(node, Component) for node in self._graph.nodes)

        # Check the types of the edge data
        data_keys = [
            a for b in map(lambda edge: list(edge[2].keys()), self._graph.edges.data()) for a in b
        ]
        data_values = [
            a for b in map(lambda edge: list(edge[2].values()), self._graph.edges.data()) for a in b
        ]
        edge_type_check = all(isinstance(x, list) for x in data_keys) and all(
            isinstance(x, list) for x in data_values
        )

        return node_type_check and edge_type_check

    def get_internal_graph(self, *, copy: bool = True) -> nx.Graph:
        """Get the internal networkx Graph of the ComponentGraph.
        Only use `copy = False` for read access. The internal graph should not be edited directly.

        :param copy: Whether to return a copy of the graph, defaults to True
        :type copy: bool, optional
        :return: The internal graph.
        :rtype: nx.Graph
        """
        if not copy:
            return self._graph
        return cp.deepcopy(self._graph)
