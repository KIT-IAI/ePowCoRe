from ast import literal_eval as make_tuple
from dataclasses import dataclass, field
import networkx as nx

from epowcore.gdf.data_structure import DataStructure, _get_class
from epowcore.gdf.port import Port
from epowcore.generic.component_graph import ComponentGraph
from epowcore.generic.logger import Logger

from .component import Component


# The attributes are never changed after being insterted into a structure requiring hashes
@dataclass
class Subsystem(Component):
    """Generic class for subsystem components. Used as an intermediate class in preparation for export."""

    graph: ComponentGraph = field(default_factory=ComponentGraph)
    """Subgraph containing the components"""

    def get_connected_to_port(self, component_id: int) -> list[Component]:
        """Get a list of components that are connected to the Port
        whose connection_component equals [component_id].

        :param component_id: The id of the Component that is represented by a Port in this Subsystem.
        :type component_id: int
        :return: The list of components in the Subsystem connected to the Port.
        :rtype: list[Component]
        """
        result: list[Component] = []
        ports = {n.connection_component: n for n in self.graph.nodes if isinstance(n, Port)}
        port = ports[component_id]

        for n in self.graph.neighbors(port):
            result.append(n)

        return result

    @classmethod
    def from_components(
        cls,
        data_structure: DataStructure,
        components: list[Component],
        update_ds: bool = True,
        name: str | None = None,
    ) -> "Subsystem":
        """Create a subsystem from a list of components and optionally update the data structure.

        :param data_structure: The data structure that contains the given components.
        :type data_structure: DataStructure
        :param components: The components that form the new subsystem.
        :type components: list[Component]
        :param update_ds: If True, the components are removed from the data structure and replaced with the subsystem; defaults to True
        :type update_ds: bool, optional
        :raises ValueError: Raised when parameters are not allowed.
        :return: The new Subsystem component containing the given Component list.
        :rtype: Subsystem
        """

        # Create subgraph
        graph = ComponentGraph()
        for component in components:
            graph.add_node(component)

        coords = next((x.coords for x in components if x.coords is not None), None)
        if name is None:
            name = f"{components[0].name}"
        subsystem = cls(data_structure.get_valid_id(), name, coords, graph)

        subsystem.__add_edges_and_ports(data_structure, components)

        if not update_ds:
            return subsystem
        subsystem.__replace_in_data_structure(data_structure, components)
        Logger.log_to_selected(
            f"Created subsystem from components {[(c.uid, type(c).__name__) for c in components]}"
        )
        return subsystem

    def to_primitive_dict(self) -> dict:
        """Return the dataclass as a dict containing only primitive data types.

        :return: A dictionary describing the instance with primitive data types only.
        :rtype: dict
        """
        normal_dict = super().to_primitive_dict()
        del normal_dict["graph"]
        return normal_dict | self.graph.to_primitive_dict()

    @classmethod
    def from_primitive_dict(cls, data: dict) -> Component:
        """Override the default from_primitive_dict method to handle the graph."""
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
        if "connector_names" in import_data:
            del import_data["connector_names"]

        if not "coords" in import_data.keys():
            import_data["coords"] = None
        elif import_data["coords"] is not None:
            if all(isinstance(i, list) for i in import_data["coords"]):
                # list of coordinates
                import_data["coords"] = [tuple(i) for i in import_data["coords"]]
            else:
                # only one pair of coordinates
                import_data["coords"] = tuple(import_data["coords"])

        return cls(**import_data)

    def get_max_id(self) -> int:
        """Get the highest assigned component id in this Subsystem.
        Recursively scans included Subsystems.

        :return: The biggest component id found in this and subsequent Subsystems.
        :rtype: int
        """
        if len(self.graph.nodes) == 0:
            return 0
        max_id = max(n.uid for n in self.graph.nodes)
        for s in [n for n in self.graph.nodes if isinstance(n, Subsystem)]:
            s_max = s.get_max_id()
            if s_max > max_id:
                max_id = s_max
        return max_id

    def get_component_by_id(self, uid: int) -> tuple[Component | None, ComponentGraph | None]:
        """Get a component by its uid.

        :param uid: The uid of the component.
        :type uid: int
        :return: The component.
        :rtype: Component
        """
        for component in self.graph.nodes:
            if component.uid == uid:
                return component, self.graph
            if isinstance(component, Subsystem):
                result, graph = component.get_component_by_id(uid)
                if result is not None:
                    return result, graph
        return None, None

    def __add_edges_and_ports(
        self,
        data_structure: DataStructure,
        components: list[Component],
    ) -> None:
        """Add edges and ports to the subsystem.

        :param data_structure: The data structure containing the components.
        :param components: The components that are part of the subsystem.
        :param graph: The graph of the subsystem, already containing the components.
        """
        uids = [x.uid for x in components]
        # keep track of added ports to only add one port per external component (neighbor)
        added_ports: dict[int, Port] = {}
        for component in components:
            neighbors = list(data_structure.graph.neighbors(component))
            for neighbor in neighbors:
                edge_data: dict = data_structure.graph.edges[component, neighbor]  # type: ignore
                if not neighbor.uid in uids:
                    # Connection is not part of the subsystem
                    if neighbor.uid not in added_ports:
                        port = Port(
                            self.uid + len(added_ports) + 1,
                            f"Port {neighbor.uid}",
                            None,
                            neighbor.uid,
                        )
                        self.graph.add_node(port)
                        added_ports[neighbor.uid] = port
                    else:
                        port = added_ports[neighbor.uid]
                    self.graph.add_edge(component, port)

                    new_edge_data: dict[int, list[str]] = {}
                    if component.uid in edge_data:
                        new_edge_data[component.uid] = edge_data[component.uid]
                    if neighbor.uid in edge_data:
                        new_edge_data[port.uid] = edge_data[neighbor.uid]

                    self.graph.edges.update(component, port, new_edge_data)
                else:
                    self.graph.add_edge(component, neighbor)
                    self.graph.edges.update(component, neighbor, edge_data)

    def __replace_in_data_structure(
        self,
        data_structure: DataStructure,
        components: list[Component],
    ) -> None:
        """
        Remove the components from the data structure.
        :param data_structure: The data structure containing the components.
        :param components: The components that are part of the subsystem.
        :param subsystem: The subsystem that replaces the components.
        """
        edges = {}
        uids = [x.uid for x in components]
        for component in components:
            if component not in data_structure.graph.nodes:
                Logger.log_to_selected(f"Component {component.uid} not found in data structure")
                continue
            edges[component.uid] = list(data_structure.graph.edges.data(component))
            data_structure.graph.remove_node(component)

        data_structure.add_component(self)

        # Reattach edges with data
        for component in components:
            for left, right, data in edges[component.uid]:
                neighbor: Component = right if left.uid == component.uid else left
                if neighbor.uid in uids:
                    continue

                subsys_data = None
                neighbor_data = None
                if component.uid in data:
                    subsys_data = data[component.uid]
                if neighbor.uid in data:
                    neighbor_data = data[neighbor.uid]

                data_structure.add_connection(self, neighbor, subsys_data, neighbor_data)

    def __hash__(self) -> int:
        return hash((self.uid, type(self), self.graph))

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Subsystem):
            return False
        return super().__eq__(__value) and self.graph == __value.graph
