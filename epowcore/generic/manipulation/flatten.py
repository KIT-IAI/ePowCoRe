from epowcore.gdf.component import Component
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.port import Port
from epowcore.gdf.subsystem import Subsystem


def flatten(data_structure: DataStructure, iterative: bool = True) -> None:
    """Remove all subsystems from the data structure and merge their content
    into the data structure itself.
    """
    while True:
        subsystems = data_structure.type_list(Subsystem)
        if not subsystems:
            return
        for subsystem in subsystems:
            # Insert subsystem graph into data structure
            for component in subsystem.graph.nodes:
                data_structure.add_component(component)
            for left, right, data in subsystem.graph.edges.data():
                left_data = data.get(left.uid, "")
                right_data = data.get(right.uid, "")
                data_structure.add_connection(left, right, left_data, right_data)

            # Remove ports and replace them with connections to their associated components
            for port in data_structure.type_list(Port):
                subsystem_neighbor = __find_subsystem_neighbor(port, subsystem, data_structure)
                if subsystem_neighbor is None:
                    continue
                neighbors = list(data_structure.graph.neighbors(port))
                for port_neighbor in neighbors:
                    # what is the connection name at the internal component?
                    port_neighbor_data = data_structure.get_connection_name(port, port_neighbor)
                    # what is the connection name at the port and thus at the external component?
                    port_data = data_structure.get_connection_name(port_neighbor, port)

                    data_structure.add_connection(
                        subsystem_neighbor, port_neighbor, port_data, port_neighbor_data
                    )
                data_structure.remove_component(port)
            data_structure.remove_component(subsystem)
        if not iterative:
            return


def __find_subsystem_neighbor(
    port: Port, subsystem: Subsystem, data_structure: DataStructure
) -> Component | None:
    return next(
        (
            x
            for x in data_structure.graph.neighbors(subsystem)
            if x.uid == port.connection_component
        ),
        None,
    )
