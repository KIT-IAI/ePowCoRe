from epowcore.gdf.bus import Bus, BusType, LFBusType
from epowcore.gdf.component import Component
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.switch import Switch
from epowcore.gdf.tline import TLine
from epowcore.generic.logger import Logger
from epowcore.generic.manipulation.merge_components import merge_components


def __skip_component(
    from_component: Component,
    to_component: Component,
    dont_connect: tuple[type, ...],
) -> bool:
    if isinstance(from_component, Bus) and isinstance(to_component, Bus):
        return True
    if isinstance(from_component, (Bus, TLine, Switch)) or isinstance(
        to_component, (Bus, TLine, Switch)
    ):
        return True
    if isinstance(from_component, dont_connect) or isinstance(to_component, dont_connect):
        return True
    return False


def __get_bus_bar(
    data_structure: DataStructure,
    from_component: Component,
    to_component: Component,
    edge_data: dict[int, list[str]],
    bus_dict: dict,
) -> tuple[Bus, int]:
    bus_bar_id = data_structure.get_valid_id()
    bus_bar = None

    if not from_component.uid in edge_data:
        edge_data[from_component.uid] = []
    if not to_component.uid in edge_data:
        edge_data[to_component.uid] = []

    from_has_bus = (
        from_component.uid,
        "".join(edge_data[from_component.uid]),
    ) in bus_dict
    to_has_bus = (
        to_component.uid,
        "".join(edge_data[to_component.uid]),
    ) in bus_dict

    if from_has_bus and to_has_bus:
        from_bus_id = bus_dict[(from_component.uid, "".join(edge_data[from_component.uid]))]
        bus_bar = data_structure.get_component_by_id(from_bus_id)[0]
        to_bus_id = bus_dict[(to_component.uid, "".join(edge_data[to_component.uid]))]
        bus_bar_to = data_structure.get_component_by_id(to_bus_id)[0]
        if bus_bar is None or bus_bar_to is None:
            raise ValueError(f"Component {to_bus_id} or {from_bus_id} not found")

        merge_components(
            data_structure,
            bus_bar,
            bus_bar_to,
        )
        for bus_id in bus_dict.values():
            if bus_id == to_bus_id:
                bus_id = from_bus_id
    elif from_has_bus or to_has_bus:
        b = from_component if from_has_bus else to_component
        from_bus_id = bus_dict[(b.uid, "".join(edge_data[b.uid]))]
        bus_bar_id = bus_dict[(b.uid, "".join(edge_data[b.uid]))]
        bus_bar = data_structure.get_component_by_id(from_bus_id)[0]
    else:
        bus_bar = Bus(
            bus_bar_id,
            f"BusBar_{bus_bar_id}",
            None,
            nominal_voltage=0.0,
            lf_bus_type=LFBusType.PQ,
            bus_type=BusType.BUSBAR,
        )
        data_structure.add_component(bus_bar)

    if not isinstance(bus_bar, Bus):
        raise ValueError(f"Component {bus_bar_id} is not a Bus")

    return bus_bar, bus_bar_id


def __update_edges(
    data_structure: DataStructure,
    from_component: Component,
    to_component: Component,
    bus_bar: Bus,
    edge_data: dict,
) -> None:
    data_structure.graph.add_edge(from_component, bus_bar)
    data_structure.graph.add_edge(bus_bar, to_component)

    edge_data_from = {from_component.uid: edge_data[from_component.uid]}
    edge_data_to = {to_component.uid: edge_data[to_component.uid]}
    data_structure.graph.edges.update(from_component, bus_bar, edge_data_from)
    data_structure.graph.edges.update(bus_bar, to_component, edge_data_to)

    data_structure.graph.remove_edge(from_component, to_component)


def insert_buses(
    data_structure: DataStructure, dont_connect: tuple[type, ...] | None = None
) -> None:
    """Insert buses between components that are not connected to a bus.

    :param data_structure: The data structure to insert the buses into.
    :type data_structure: DataStructure
    :param dont_connect: A list of components that should not be connected to a bus.
    :type dont_connect: tuple[type, ...]
    """
    if dont_connect is None:
        dont_connect = ()
    bus_dict: dict[tuple[int, str], int] = {}
    for from_component, to_component in list(data_structure.graph.edges()):
        if __skip_component(from_component, to_component, dont_connect):
            continue
        edge_data = data_structure.graph[from_component][to_component]
        bus_bar, bus_bar_id = __get_bus_bar(
            data_structure, from_component, to_component, edge_data, bus_dict
        )
        __update_edges(data_structure, from_component, to_component, bus_bar, edge_data)
        bus_dict[(from_component.uid, "".join(edge_data[from_component.uid]))] = bus_bar_id
        bus_dict[(to_component.uid, "".join(edge_data[to_component.uid]))] = bus_bar_id
        Logger.log_to_selected(
            f"Inserted bus bar ({bus_bar.uid}) between {from_component.name} and {to_component.name}"
        )
