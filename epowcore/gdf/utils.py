from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.port import Port
from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.component_graph import ComponentGraph

from .bus import Bus


def get_connected_bus(graph: ComponentGraph, node: Component, max_depth: int = 3) -> Bus | None:
    """Search for the nearest bus connected to the given node with maximum search depth.

    :param graph: The graph to search in.
    :type graph: nx.Graph
    :param node: The node to start the search from.
    :type node: Component
    :param max_depth: The maximum search depth.
    :type max_depth: int
    """
    seen = {}
    queue = [node]
    for i in range(max_depth):
        next_queue: list[Component] = []
        for component in queue:
            for neighbor in graph.neighbors(component):
                if isinstance(neighbor, Bus):
                    return neighbor
                if isinstance(neighbor, Subsystem):
                    return next(
                        (
                            get_connected_bus(neighbor.graph, port, max_depth - i)
                            for port in neighbor.graph.nodes
                            if isinstance(port, Port) and port.connection_component == component.uid
                        ),
                        None,
                    )
                if neighbor not in seen:
                    seen[neighbor] = True
                    next_queue.append(neighbor)
        queue = next_queue

    return None

def get_z_base(component: Component, core_model: CoreModel) -> float:
    """Calculate the base impedance (z_base) with the voltage of a connected bus and the base rating.

    :param component: The component to get the connected bus for
    :type component: Component
    :param core_model: The CoreModel containing the component
    :type core_model: CoreModel
    :return: The base rating [MVA]
    :rtype: float
    """
    connected_bus = get_connected_bus(core_model.graph, component)
    if connected_bus is None:
        raise ValueError(f"Could not find connected bus for line {component.uid}")
    u_base = connected_bus.nominal_voltage
    z_base = u_base**2 / core_model.base_mva_fb()
    return z_base
