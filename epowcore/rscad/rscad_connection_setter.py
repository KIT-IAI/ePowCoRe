"""This module is responsible for setting and removing the connections between RSCAD components"""

from collections import Counter
from copy import deepcopy
from typing import get_args

from pyapi_rts.api import Subsystem, Component
from pyapi_rts.generated.BUS import BUS
from pyapi_rts.generated.WIRE import WIRE
from pyapi_rts.generated.wirelabel import wirelabel
from pyapi_rts.generated.enums.Noyes2EnumParameter import Noyes2Enum

from epowcore.rscad.constants import (
    CONNECTION_DICTIONARY,
    GRID_OFFSET,
    GRID_STEP_SIZE,
    RSCADPSS,
    RSCADExciters,
)


def set_on_connection_point(
    connections: dict[str, list[tuple[Component, list[str]]]],
    component: Component,
    subsystem: Subsystem,
) -> list[Component]:
    """Chooses the connection method by the type of component and returns
    the newly created buses from the methods"""
    # Component is a two winding transformer
    if component.type == "_rtds_3P2W_TRF.def":
        return _connect_2w_transformer(connections, component, subsystem)
    # Component is a three winding transformer
    if component.type == "_rtds_3P3W_TRF.def":
        return _connect_3w_transformer(connections, component, subsystem)
    if component.type in ("lf_rtds_sharc_sld_SERIESRLC", "_rtds_PI123.def"):
        return _connect_two_connection_component(connections, component, subsystem)
    return []


def remove_single_bus_links(subsystem: Subsystem) -> None:
    """Remove the linked Node attribute from buses that
    have only one instance of their name in the graph
    or buses that are not connected to any other buses.
    """

    graph, _ = subsystem.get_graph()

    # group buses by name in a dictionary
    components = subsystem.get_components(recursive=True, clone=False, with_groups=True)
    buses = [c for c in components if c.type == "rtds_sharc_sld_BUSLABEL"]
    bus_dict: dict[str, list[Component]] = {bus.name: [] for bus in buses}
    for bus in buses:
        bus_dict[bus.name].append(bus)

    for _, bs in bus_dict.items():
        if len(bs) == 1:
            # if there is only one buslabel with this name -> not linked
            bs[0].Parameters.linkNodes.value = Noyes2Enum.No # type: ignore
        else:
            # if multiple buslabels with this name, check the graph if there are linked connections
            link_found = False
            for _, _, data in graph.edges(bs[0].uuid, data="type"): # type: ignore
                if data == "LINK_CONNECTED":
                    link_found = True
                    break
            if not link_found:
                for b in bs:
                    b.Parameters.linkNodes.value = Noyes2Enum.No # type: ignore


def get_connection_point_coordinates(
    component: Component, connection_point: str
) -> tuple[int, int]:
    """Returns the x-,y-coordinates of the given component at the given connectionPoint"""
    point = component.connection_points.get(connection_point)
    if point is None:
        raise ValueError(
            f"Could not find connection point {connection_point} in component {component.name} ({component.type})"
        )
    position_tuple = point.position_abs
    return position_tuple


def create_bus_connection(start: tuple[int, int], end: tuple[int, int], orientation: str) -> BUS:
    """Create a bus connection with the given specifications."""
    connection = BUS()
    # Standard direction is from x direction going from left to right
    if orientation == "y":
        connection.rotation = 1
    connection.x = start[0]
    connection.y = start[1]
    connection.HIDDENPARAMETERS.x2.value = end[0] - start[0]
    return connection


def set_wire_points_generator_box(
    components: list[Component], connected_to: tuple[int, int]
) -> list[Component]:
    """Set all wire labels in the generator_box described by the given components."""
    connections: list[tuple[str, str]] = []
    # aggregate all newly created elements
    additional_connections = []
    pss_in_generator_box = Noyes2Enum.No
    # Reset Connection point dictionary
    connection_point_dict = deepcopy(CONNECTION_DICTIONARY)

    # Get the intersection of the connection points in elements
    # I.e. connection points that are present on multiple components
    for component in components:
        connections += connection_point_dict.get(component.type, [])
        if isinstance(component, get_args(RSCADPSS)):
            pss_in_generator_box = Noyes2Enum.Yes
    intersecting_connections = _get_intersecting_connections(connections)

    if pss_in_generator_box == Noyes2Enum.No:
        # No PSS present -> remove the corresponding connections
        for exc in get_args(RSCADExciters):
            exc_conns = connection_point_dict[exc.type]
            # get the relevant PSS connections
            pss_conns = [c for c in exc_conns if c[1] == "Vs"]
            for pss_conn in pss_conns:
                connection_point_dict[exc.type].remove(pss_conn)

    # Set the the wire labels for the control elements and generator
    for component in components:
        filtered = _filter_connections(
            connection_point_dict.get(component.type, []),
            intersecting_connections,
        )
        if isinstance(component, get_args(RSCADExciters)):
            # (de)activate PSS connection
            component.CONFIGURATION.PSS.value = pss_in_generator_box  # type: ignore

        if component.type == "lf_rtds_sharc_sld_MACV31":
            bus_connection = get_connection_point_coordinates(component, "A_1")
            # Set connection from Generator to Bus
            bus_line = _set_bus_line(
                (bus_connection[0] + GRID_STEP_SIZE, bus_connection[1]),
                connected_to,
            )
            additional_connections += _set_wire_points(component, filtered) + [bus_line]
        elif component.type == "_rtds_IEEEG1.def":
            additional_connections += _set_wire_points(
                component, filtered, suffix=component.get_by_key("Ghp")
            )
        else:
            additional_connections += _set_wire_points(component, filtered)

    return additional_connections


def _connect_2w_transformer(
    connections: dict[str, list[tuple[Component, list[str]]]],
    trafo: Component,
    subsystem: Subsystem,
) -> list[Component]:
    """Set the connection of the appropriate buses with the given two-winding transformer."""
    # Look up the buses connected to the trafo
    bus_connections = connections[trafo.uuid]
    # Cordinates of the connection points of the trafo
    connection_coordinates: dict[str, tuple[int, int]] = {}
    connection_coordinates["HV"] = get_connection_point_coordinates(trafo, "A_1")
    connection_coordinates["LV"] = get_connection_point_coordinates(trafo, "A_2")
    # List collecting duplicated buses
    new_labels: list[Component] = []
    # Set bus connection on the winding connection point of the transformer
    for bus, connection_names in bus_connections:
        for connection_name in connection_names:
            _place_bus(bus, connection_coordinates[connection_name], subsystem, new_labels)
    return new_labels


def _connect_3w_transformer(
    connections: dict[str, list[tuple[Component, list[str]]]],
    trafo: Component,
    subsystem: Subsystem,
) -> list[Component]:
    """Set the connection of the appropriate buses with the given three-winding transformer."""
    # Look up the buses connected to the trafo
    bus_connections = connections[trafo.uuid]
    # Cordinates of the connection points of the trafo
    connection_coordinates: dict[str, tuple[int, int]] = {}
    connection_coordinates["HV"] = get_connection_point_coordinates(trafo, "A_1")
    connection_coordinates["MV"] = get_connection_point_coordinates(trafo, "A_2")
    connection_coordinates["LV"] = get_connection_point_coordinates(trafo, "A_3")
    # List collecting duplicated buses
    new_labels: list[Component] = []
    # Set bus connection on the winding connection point of the transformer
    for bus, connection_names in bus_connections:
        for connection_name in connection_names:
            _place_bus(bus, connection_coordinates[connection_name], subsystem, new_labels)
    return new_labels


def _connect_two_connection_component(
    connections: dict[str, list[tuple[Component, list[str]]]],
    component: Component,
    subsystem: Subsystem,
) -> list[Component]:
    """Connects two buses with each other. Possible components must have only two connections and
    no restriction which bus is placed on which connection"""
    bus_connections = connections[component.uuid]
    connection1 = get_connection_point_coordinates(component, "A_1")
    connection2 = get_connection_point_coordinates(component, "A_2")
    new_labels: list[Component] = []
    bus1 = bus_connections[0][0]
    bus2 = bus_connections[1][0]
    # Swap if labels A_1 and A_2 are assigned to the wrong bus
    a1_exists = None
    a2_exists = None
    for bus, connection_name in bus_connections:
        if connection_name == "A_1":
            a1_exists = bus
        elif connection_name == "A_2":
            a2_exists = bus
        if a1_exists is not None and a2_exists is not None:
            bus1 = a1_exists
            bus2 = a2_exists
            break

    _place_bus(bus1, connection1, subsystem, new_labels)
    _place_bus(bus2, connection2, subsystem, new_labels)

    return new_labels


def _place_bus(
    bus: Component, position: tuple[int, int], subsystem: Subsystem, new_labels: list[Component]
) -> None:
    """Place a bus at the given position. Create a ducplicate of the bus if it is already in use."""
    if not bus.x == GRID_OFFSET + GRID_STEP_SIZE * 4:
        # buslabel is not in its original position and thus already used
        bus = bus.duplicate(new_id=True)
        subsystem.add_component(bus)
        new_labels.append(bus)

    bus.x = position[0]
    bus.y = position[1]


def _set_bus_line(
    connection_point: tuple[int, int],
    connected_to: tuple[int, int],
) -> BUS:
    """Set the orientation of the bus line from the (x,y)-coordinates connectionPoint to connectedTo"""
    start = connection_point
    end = connected_to
    orientation = "x"
    if connection_point[0] < connected_to[0]:
        orientation = "x"
    if connection_point[1] < connected_to[1]:
        orientation = "y"
    if connection_point[0] > connected_to[0]:
        start = connected_to
        end = connection_point
        orientation = "x"
    if connection_point[1] > connected_to[1]:
        start = connected_to
        end = connection_point
        orientation = "y"
    return create_bus_connection(start, end, orientation)


def _set_wire_points(
    component: Component,
    connection_points: list[tuple[str, str]],
    suffix: str | None = None,
) -> list[Component]:
    """Creates wire labels and wires for the given connection points and returns those"""
    additional_components = []
    if suffix is None:
        suffix = component.name
    for connection_type in connection_points:
        connection = get_connection_point_coordinates(component, connection_type[0])
        connection_rotation = _get_component_side(connection[0], connection[1], component)
        additional_components += _set_wire_label(
            connection, connection_rotation, connection_type[1] + suffix
        )
    return additional_components


def _set_wire_label(
    connection_coordinate: tuple[int, int], rotation: str, label_name: str
) -> list[Component]:
    """Creates a wire Label and returns a list containing the wire Label and its wire"""
    wire_label_x = connection_coordinate[0]
    wire_label_y = connection_coordinate[1]

    orientation = "x"
    mirror = False

    # Set the location of the wire label
    if rotation == "DOWN":
        wire_label_y += GRID_STEP_SIZE
        orientation = "y"
        mirror = True
    elif rotation == "UP":
        wire_label_y -= GRID_STEP_SIZE
        orientation = "y"
        mirror = False
    elif rotation == "LEFT":
        wire_label_x -= GRID_STEP_SIZE
        orientation = "x"
        mirror = False
    elif rotation == "RIGHT":
        wire_label_x += GRID_STEP_SIZE
        orientation = "x"
        mirror = True
    # Create the wire label
    wire_label = wirelabel()
    wire_label.x = wire_label_x
    wire_label.y = wire_label_y
    wire_label.Name.value = label_name
    wire = _create_wire_connection(orientation, wire_label_x, wire_label_y, GRID_STEP_SIZE, mirror)
    return [wire_label, wire]


def _create_wire_connection(
    orientation: str,
    x_position: int,
    y_position: int,
    length: int,
    mirror: bool = False,
) -> WIRE:
    """Create a bus connection with the given specifications"""
    connection = WIRE()
    # Standard direction is from x direction going from left to right
    if orientation == "y":
        connection.rotation = 1
    if orientation == "x":
        connection.rotation = 0
    connection.x = x_position
    connection.y = y_position
    if mirror:
        connection.mirror = 1
    connection.HIDDENPARAMETERS.x2.value = length
    return connection


def _get_component_side(
    connection_point_x: int, connection_point_y: int, component: Component
) -> str:
    """Return the side of the connection point in relation to its component.
    The position strings represent the location relative to the component"""
    component_borders = component.bounding_box_abs
    if connection_point_y >= component.y and connection_point_y >= component_borders[3]:
        return "DOWN"
    if connection_point_y <= component.y and connection_point_y <= component_borders[1]:
        return "UP"
    if connection_point_x <= component.x and connection_point_x <= component_borders[0]:
        return "LEFT"
    if connection_point_x >= component.x and connection_point_x >= component_borders[2]:
        return "RIGHT"
    raise ValueError("Could not determine the side of the connection point")


def _get_intersecting_connections(connections: list[tuple[str, str]]) -> list[str]:
    """Return a list of every non-unique connection point inside the given list of
    connection tuples and specific generator signals that have no connection point.
    """
    all_connection_types = [connection[1] for connection in connections]
    counts = Counter(all_connection_types)
    # Additional Signals from the Generator.
    # TODO: Check which signals are useful for various controlelements
    optional = ("PMACH", "QMACH")
    intersecting_connections = [
        id for id in all_connection_types if counts[id] > 1 or id in optional
    ]
    return intersecting_connections


def _filter_connections(
    connections: list[tuple[str, str]], intersecting_connections: list[str]
) -> list[tuple[str, str]]:
    """Filter the list of connections to only include the intersecting connections."""
    filtered = [
        connection for connection in connections if connection[1] in intersecting_connections
    ]
    return filtered
