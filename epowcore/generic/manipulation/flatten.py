from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.port import Port
from epowcore.gdf.subsystem import Subsystem


def flatten(core_model: CoreModel, iterative: bool = True) -> None:
    """Remove all subsystems from the core model and merge their content
    into the core model itself.
    """
    while True:
        subsystems = core_model.type_list(Subsystem)
        if not subsystems:
            return
        for subsystem in subsystems:
            # Insert subsystem graph into core model
            for component in subsystem.graph.nodes:
                core_model.add_component(component)
            for left, right, data in subsystem.graph.edges.data():
                left_data = data.get(left.uid, "")
                right_data = data.get(right.uid, "")
                core_model.add_connection(left, right, left_data, right_data)

            # Remove ports and replace them with connections to their associated components
            for port in core_model.type_list(Port):
                subsystem_neighbor = __find_subsystem_neighbor(port, subsystem, core_model)
                if subsystem_neighbor is None:
                    continue
                neighbors = list(core_model.graph.neighbors(port))
                for port_neighbor in neighbors:
                    # what is the connection name at the internal component?
                    port_neighbor_data = core_model.get_connection_name(port, port_neighbor)
                    # what is the connection name at the port and thus at the external component?
                    port_data = core_model.get_connection_name(port_neighbor, port)

                    core_model.add_connection(
                        subsystem_neighbor, port_neighbor, port_data, port_neighbor_data
                    )
                core_model.remove_component(port)
            core_model.remove_component(subsystem)
        if not iterative:
            return


def __find_subsystem_neighbor(
    port: Port, subsystem: Subsystem, core_model: CoreModel
) -> Component | None:
    return next(
        (
            x
            for x in core_model.graph.neighbors(subsystem)
            if x.uid == port.connection_component
        ),
        None,
    )
