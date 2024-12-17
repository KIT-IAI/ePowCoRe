import unittest

import networkx as nx

from epowcore.gdf.component import Component
from epowcore.generic.component_graph import ComponentGraph


class ComponentGraphTest(unittest.TestCase):
    """Tests the basic functionality of the ComponentGraph."""

    def test_add_node(self) -> None:
        tgraph = ComponentGraph()
        node = Component(0, "One", None)
        tgraph.add_node(node)

        graph = tgraph.get_internal_graph()
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(len(tgraph.nodes), 1)

    def test_add_edge(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        tgraph.add_edge(node1, node2)

        graph = tgraph.get_internal_graph()
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 1)

    def test_remove_node_1(self) -> None:
        tgraph = ComponentGraph()
        node = Component(0, "One", None)
        tgraph.add_node(node)

        tgraph.remove_node(node)

        graph = tgraph.get_internal_graph()
        self.assertEqual(len(graph.nodes), 0)

    def test_remove_node_2(self) -> None:
        tgraph = ComponentGraph()
        node = Component(0, "One", None)
        with self.assertRaises(nx.NetworkXError):
            tgraph.remove_node(node)

        graph = tgraph.get_internal_graph()
        self.assertEqual(len(graph.nodes), 0)

    def test_nodes_contains(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        tgraph.add_node(node1)

        self.assertTrue(node1 in tgraph.nodes)
        self.assertTrue(node2 not in tgraph.nodes)

    def test_nodes_iterator(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        tgraph.add_node(node1)
        tgraph.add_node(node2)

        count = 0
        for _ in tgraph.nodes:
            count += 1
        self.assertEqual(count, 2)

    def test_nodes_get(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        tgraph.add_node(node1)

        self.assertEqual(tgraph.nodes[node1], {})
        with self.assertRaises(KeyError):
            tgraph.nodes[node2]

    def test_nodes_len(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        tgraph.add_node(node1)
        tgraph.add_node(node2)

        self.assertEqual(len(tgraph.nodes), 2)

    def test_edges_contains(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        node3 = Component(2, "Three", None)
        tgraph.add_edge(node1, node2)
        tgraph.add_node(node3)

        self.assertTrue((node1, node2) in tgraph.edges)
        self.assertTrue((node2, node1) in tgraph.edges)
        self.assertTrue((node3, node2) not in tgraph.edges)

    def test_edges_iterator(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        node3 = Component(2, "Three", None)
        tgraph.add_edge(node1, node2)
        tgraph.add_edge(node2, node3)

        count = 0
        for _ in tgraph.edges:
            count += 1
        self.assertEqual(count, 2)

    def test_edges_get(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        node3 = Component(2, "Three", None)
        tgraph.add_edge(node1, node2)

        self.assertEqual(tgraph.edges[node1, node2], {})  # type: ignore
        with self.assertRaises(KeyError):
            tgraph.edges[node2, node3]  # type: ignore

    def test_edges_len(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        node3 = Component(2, "Three", None)
        tgraph.add_edge(node1, node2)
        tgraph.add_edge(node2, node3)

        self.assertEqual(len(tgraph.edges), 2)

    def test_sanity_check(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        node3 = Component(2, "Three", None)
        tgraph.add_edge(node1, node2)
        tgraph.add_edge(node2, node3)
        self.assertTrue(tgraph.sanity_check())

    def test_relabel_nodes(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        node3 = Component(2, "Three", None)
        tgraph.add_node(node1)
        tgraph.add_node(node2)
        mapping = {node1: node2, node2: node3}
        tgraph.relabel_nodes(mapping)
        self.assertEqual(tgraph.nodes[node2], {})
        self.assertEqual(tgraph.nodes[node3], {})
        self.assertEqual(len(tgraph.nodes), 2)
        self.assertEqual(len(tgraph.edges), 0)

    def test_edges_call(self) -> None:
        tgraph = ComponentGraph()
        node1 = Component(0, "One", None)
        node2 = Component(1, "Two", None)
        node3 = Component(2, "Three", None)

        tgraph.add_edge(node1, node2)
        tgraph.add_edge(node2, node3)

        edges_with_2 = list(tgraph.edges(node2))
        self.assertEqual(len(edges_with_2), 2)
        self.assertIn(node2, edges_with_2[0])
        self.assertIn(node2, edges_with_2[1])

        edges_with_1 = list(tgraph.edges(node1))
        self.assertEqual(len(edges_with_1), 1)
        self.assertIn(node1, edges_with_1[0])


if __name__ == "__main__":
    unittest.main()
