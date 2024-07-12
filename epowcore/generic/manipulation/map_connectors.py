from epowcore.gdf.component import Component
from epowcore.gdf.data_structure import DataStructure


def map_connectors(
    data_struct: DataStructure, component: Component, connector_map: dict
) -> dict[str, list[tuple[int, list[str]]]]:
    """Map the connectors of a component to other connectors.

    :param component: The component.
    :type component: Component
    :param connector_map: A dictionary mapping the connectors in the form \"gdf-connector:output\"
    :type connector_map: dict[str, list[tuple[int, str]]]
    :return: A dictionary mapping the connectors in the form \"gdf-connector-name:[(connected_id_1, port_1), (connected_id_2, port_2) ...]\"
    """

    result: dict[str, list[tuple[int, list[str]]]] = {}
    for conn_name in data_struct.get_connector_names(component):
        attached = data_struct.get_attached_to(component, conn_name)
        for attached_component, connector_name in attached:
            entry = (attached_component.uid, connector_name)
            if conn_name in connector_map.keys():
                if connector_map[conn_name] in result:
                    result[connector_map[conn_name]].append(entry)
                else:
                    result[connector_map[conn_name]] = [entry]
    for attached_component, connector_name in data_struct.get_attached_to(
        component, ""
    ):
        entry = (attached_component.uid, connector_name)
        if "" in result:
            result[""].append(entry)
        else:
            result[""] = [entry]
    return result
