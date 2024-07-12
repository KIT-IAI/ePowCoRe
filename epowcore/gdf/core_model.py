from ast import literal_eval as make_tuple
from dataclasses import dataclass, field, asdict
import importlib
from typing import TypeVar

import networkx as nx
from epowcore.generic.component_graph import ComponentGraph
from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import GDF_VERSION, Platform
from epowcore.generic.logger import Logger

from .component import Component

T = TypeVar("T")


@dataclass(kw_only=True)
class CoreModel:
    """This class represents the generic model, including the component graph and additional attributes."""

    base_frequency: float
    """Base Frequency of the elements based of the project."""
    base_mva: float | None = None
    """Base rating for pu calculations in the project."""
    graph: ComponentGraph = field(default_factory=ComponentGraph)
    """Graph of connection between elements."""
    version: int = GDF_VERSION
    """Version of the generic data format."""

    def base_mva_fb(self, platform: Platform | None = None) -> float:
        """Base rating for pu calculations in the project with fallback."""
        if self.base_mva is not None:
            return self.base_mva
        default = Configuration().get_default("CoreModel", "base_mva", platform)
        if default is None:
            raise ValueError("Could not find default value for CoreModel.base_mva")
        Logger.log_to_selected(f"Using default for {type(self).__name__}: base_mva = {default}")
        return default

    def add_component(self, component: Component) -> None:
        """Add a component to the graph.

        :param component: The component to be added.
        :type component: Component
        """
        self.graph.add_node(component)

    def remove_component(self, component: Component, keep_connections: bool = False) -> None:
        """Remove a component from the graph.

        :param component: The component to be removed.
        :type component: Component
        """
        if keep_connections:
            edges: list[tuple[Component, list[str]]] = []
            for l, r, edge_data in self.graph.edges.data(component):
                neighbor = l if l.uid != component.uid else r
                if neighbor.uid in edge_data:
                    edges.append(
                        (
                            neighbor,
                            edge_data[neighbor.uid],
                        )
                    )
            for i, edge1 in enumerate(edges):
                for edge2 in edges[i + 1 :]:
                    self.add_connection(
                        edge1[0],
                        edge2[0],
                        edge1[1],
                        edge2[1],
                    )
        self.graph.remove_node(component)

    def get_component_by_id(self, uid: int) -> tuple[Component | None, ComponentGraph | None]:
        """Get a component by its uid.

        :param uid: The uid of the component.
        :type uid: int
        :return: The component.
        :rtype: Component
        """
        from epowcore.gdf.subsystem import Subsystem

        for component in self.graph.nodes:
            if component.uid == uid:
                return component, self.graph
            if isinstance(component, Subsystem):
                result, graph = component.get_component_by_id(uid)
                if result is not None:
                    return result, graph
        return None, None

    def add_connection(
        self,
        component1: Component,
        component2: Component,
        connector_name1: str | list[str] | None = "",
        connector_name2: str | list[str] | None = "",
    ) -> None:
        """Add an edge between two components to the graph.

        :param component1: The first component.
        :type component1: Component
        :param component2: The second component.
        :type component2: Component
        :param connector_name1: The name of the connector on the first component.
        :type connector_name1: str | list[str] | None
        :param connector_name2: The name of the connector on the second component.
        :type connector_name2: str | list[str] | None
        """
        # we don't want to manipulate the given lists when concatenating
        if isinstance(connector_name1, list):
            connector_name1 = connector_name1.copy()
        if isinstance(connector_name2, list):
            connector_name2 = connector_name2.copy()
        if connector_name1 is None:
            connector_name1 = []
        if connector_name2 is None:
            connector_name2 = []
        if isinstance(connector_name1, str):
            connector_name1 = [connector_name1]
        if isinstance(connector_name2, str):
            connector_name2 = [connector_name2]
        attrs = {}
        if self.graph.has_edge(component1, component2):
            attrs = self.graph.edges[component1, component2]
            if component1.uid in attrs:
                attrs[component1.uid] += connector_name1
            else:
                attrs[component1.uid] = connector_name1
            if component2.uid in attrs:
                attrs[component2.uid] += connector_name2
            else:
                attrs[component2.uid] = connector_name2
        else:
            attrs = {
                component1.uid: connector_name1,
                component2.uid: connector_name2,
            }
            self.graph.add_edge(component1, component2)
        self.graph.edges.update(component1, component2, attrs)

    # TODO This is kept for legacy reasons. Has only been used without following subsystems and ports.
    def get_attached_to(
        self,
        component: Component,
        connector_name: str | None = None,
    ) -> list[tuple[Component, list[str]]]:
        """Get the components attached to a component. Optionally filtered by connector name.

        :param component: The source component.
        :type component: Component
        :param connector_name: The name of the connector. If None, all neighbors are returned.
        :type connector_name: str
        :param include_subsystems: If True, connections to Subsystems and Ports are resolved to the component connected to this port/subsystem.
        :type include_subsystems: bool
        :return: A list of components attached to the connector and their port name.
        :rtype: list[Component, list[str]]
        """
        result: list[tuple[Component, list[str]]] = []
        if connector_name is None:
            # If no connector name is given, return all neighbors
            for c in self.graph.neighbors(component):
                # Check for connector name
                if c.uid in self.graph.edges[component, c]:
                    result.append((c, self.graph.edges[component, c][c.uid]))
                else:
                    result.append((c, [""]))
        else:
            edges = self.graph.edges.data()
            for edge in edges:
                if component.uid in edge[2] and connector_name in edge[2][component.uid]:
                    for k, value in edge[2].items():
                        if k != component.uid:
                            if edge[0].uid == component.uid:
                                result.append((edge[1], value))
                            else:
                                result.append((edge[0], value))
        return result

    def get_corresponding_connector(
        self, component: Component, neighbor: Component, connector_name: str
    ) -> str | None:
        """Get the corresponding connector name of a component to a neighbor component.

        :param component: The component.
        :param neighbor: The neighbor component.
        :param connector_name: The name of the connector.
        :return: The corresponding connector name. None if no corresponding connector exists.
        """
        if not self.graph.has_edge(component, neighbor):
            return None
        if component.uid not in self.graph.edges[component, neighbor]:
            return None
        if connector_name not in self.graph.edges[component, neighbor][component.uid]:
            return None
        index = self.graph.edges[component, neighbor][component.uid].index(connector_name)
        if len(self.graph.edges[component, neighbor][neighbor.uid]) != len(
            self.graph.edges[component, neighbor][component.uid]
        ):
            raise ValueError("The number of connectors does not match.")
        return self.graph.edges[component, neighbor][neighbor.uid][index]

    def get_connector_names(self, component: Component) -> list[str]:
        """Get the names of all connectors of a component.

        :param component: The component.
        :type component: Component
        :return: A list of connector names.
        :rtype: list[str]
        """
        edges = self.graph.edges.attr(component.uid)
        return [a for b in [x[2] for x in edges if x[2] is not None] for a in b]

    def get_connection_name(self, component: Component, neighbor: Component) -> list[str] | None:
        """Get the connector name of the neighbor.

        :param component: The component with the connector.
        :type component: Component
        :param neighbor: The component connected to the connector.
        :type neighbor: Component
        :return: The name of the connector.
        :rtype: list[str] | None
        """
        if not self.graph.has_edge(component, neighbor):
            return None
        if neighbor.uid not in self.graph.edges[component, neighbor]:
            return None
        return self.graph.edges[component, neighbor][neighbor.uid]

    def check_connectors(self, component: Component) -> bool:
        """Checks if the component only has connectors according to its type.

        :param component: The component.
        :type component: Component
        :return: True if the component only has valid connectors, else False.
        :rtype: bool
        """
        for connector in self.get_connector_names(component):
            if not connector in component.connector_names:
                return False
        return True

    def has_connected_to(self, component: Component, connector_name: str) -> bool:
        """Checks if the component has a connection to a specific connector.

        :param component: The component.
        :type component: Component
        :param connector_name: The name of the connector.
        :type connector_name: str
        :return: True if the component has a connection to the connector, else False.
        :rtype: bool
        """
        return len(self.get_attached_to(component, connector_name)) > 0

    def get_neighbors(
        self, component: Component, follow_links: bool = True, connector: str | None = None
    ) -> list[Component]:
        """Get the direct neighbors of [component].
        Can optionally traverse subsystems and restrict looking for neighbors at a specified [connector].

        :param component: The component whose neighbors are returned.
        :type component: Component
        :param follow_links: If true, replace Subsystems and Ports with the component they actually connect to; defaults to True
        :type follow_links: bool, optional
        :param connector: If not None, limit only return neighbors connected to this connector; defaults to None
        :type connector: str | None, optional
        :return: A list of components connected to to given [component].
        :rtype: list[Component]
        """
        from epowcore.gdf.subsystem import Subsystem
        from epowcore.gdf.port import Port

        _, graph = self.get_component_by_id(component.uid)
        if graph is None:
            return []

        neighbors: list[Component]

        if connector is not None:
            neighbors = []
            edge_data = graph.edges.data(component)
            for _, neighbor, data in edge_data:
                connectors = data[component.uid]
                if connector in connectors:
                    neighbors.append(neighbor)
        else:
            neighbors = list(graph.neighbors(component))

        if follow_links:
            # replace ports and subsystems as long as there are any in the list
            while any(isinstance(n, (Port, Subsystem)) for n in neighbors):
                new_neighbors = []
                for n in neighbors:
                    if isinstance(n, Port):
                        # get the component that the port represents in the subsystem
                        connected_component = self.get_component_by_id(n.connection_component)[0]
                        if connected_component is not None:
                            new_neighbors.append(connected_component)
                    elif isinstance(n, Subsystem):
                        # get the components that are connected to the corresponding port inside the subsystem
                        new_neighbors.extend(n.get_connected_to_port(component.uid))
                    else:
                        new_neighbors.append(n)
                neighbors = new_neighbors
        return neighbors

    def type_list(self, comp_type: type[T] | list[type[T]]) -> list[T]:
        """List of components of type [comp_type]."""
        if isinstance(comp_type, list):
            return [x for x in self.graph.nodes if isinstance(x, tuple(comp_type))]  # type: ignore
        return [x for x in self.graph.nodes if isinstance(x, comp_type)]

    def component_list(self) -> list[Component]:
        """List of all components."""
        return list(self.graph.nodes)

    def get_valid_id(self) -> int:
        """Generate a valid new component ID by calculating the maximum taken ID.

        :return: A valid ID for a new component.
        :rtype: int
        """
        if len(self.graph.nodes) == 0:
            return 0
        max_id = max(n.uid for n in self.graph.nodes)
        from epowcore.gdf.subsystem import Subsystem

        for s in self.type_list(Subsystem):
            s_max = s.get_max_id()
            if s_max > max_id:
                max_id = s_max
        return max_id + 1

    def sanity_check(self) -> bool:
        """Checks the validity of the model.

        :return: True if the model is valid, else False.
        """

        graph_sanity = self.graph.sanity_check()
        # Check if the edges have the required connectors
        connector_check = all(
            map(
                lambda node: len(node.connector_names) == 0
                or all(
                    map(
                        lambda x: self.has_connected_to(node, x),
                        node.connector_names,
                    )
                ),
                self.graph.nodes,
            )
        )

        # Check if the nodes have unique IDs
        unique_ids_check = len(self.graph.nodes) == len(
            set((node.uid for node in self.graph.nodes))
        )
        return graph_sanity and connector_check and unique_ids_check

    def export_dict(self) -> dict:
        """Export the whole model as a dictionary.
        The dictionary only contains primitive values and thus can be encoded as JSON.

        :return: The dictionary containing the model settings, graph, and components.
        :rtype: dict
        """
        data = asdict(self)
        del data["graph"]
        return data | self.graph.to_primitive_dict()

    @classmethod
    def import_dict(cls, data: dict) -> "CoreModel":
        """Import a valid dictionary and return a CoreModel representation of the model.

        :param data: The dictionary containing the model data.
        :type data: dict
        :return: The CoreModel representation of the model.
        :rtype: CoreModel
        """
        version = data.get("version", None)
        if version is None or version != GDF_VERSION:
            raise ValueError(
                f"Version of data doesn't match version of CoreModel: {version} != {GDF_VERSION}"
            )
        import_data = dict(data)
        import_comp_dict = data["components"]
        label_dict = {}
        class_dict = {}
        for key_str, comp_data in import_comp_dict.items():
            key = make_tuple(key_str)
            if key[0] not in class_dict:
                klass = _get_class(key[0])
                class_dict[key[0]] = klass
            else:
                klass = class_dict[key[0]]
            component = klass.from_primitive_dict(comp_data)
            label_dict[key_str] = component
        import_graph = nx.from_dict_of_dicts(import_data["graph"])
        # convert edge keys from string to int
        for _, _, d in import_graph.edges.data():
            for key, value in list(d.items()):
                if key in d and not isinstance(key, int):
                    d[int(key)] = value
                    del d[key]
        import_data["graph"] = ComponentGraph(nx.relabel_nodes(import_graph, label_dict))
        del import_data["components"]
        return cls(**import_data)


def _get_class(full_class_name: str) -> type[Component]:
    split_name = full_class_name.split(".")
    module_name = ".".join(split_name[:-1])
    class_name = split_name[-1]
    module = importlib.import_module(module_name)
    return getattr(module, class_name)
