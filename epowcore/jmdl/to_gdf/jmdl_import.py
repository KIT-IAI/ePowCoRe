from typing import Any

from epowcore.gdf import DataStructure
from epowcore.gdf.component import Component
from epowcore.gdf.port import Port as GdfPort
from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.component_graph import ComponentGraph
import epowcore.jmdl.to_gdf.components as Components
from epowcore.jmdl.jmdl_model import Block, DataType, JmdlModel, Data, Port, Root


def import_jmdl(
    jmdl: JmdlModel,
    base_data_structure: DataStructure | None = None,
    graph: ComponentGraph | None = None,
) -> DataStructure:
    """Imports a JMDLModel and converts it to a GDF DataStructure.

    :param jmdl: The JMDL object
    :type jmdl: JMDLImport
    :param base_data_structure: Required for recursive calls to keep track of IDs.
    :type base_data_structure: DataStructure | None
    :param graph: Required for recursive calls to add components to correct graph.
    :type graph: ComponentGraph | None
    """
    if graph is None:
        data_structure = DataStructure(base_frequency=jmdl.base_frequency, base_mva=jmdl.base_mva)
    else:
        data_structure = DataStructure(
            base_frequency=jmdl.base_frequency, base_mva=jmdl.base_mva, graph=graph
        )

    if base_data_structure is None:
        base_data_structure = data_structure

    components: list[Component] = __load_components(jmdl, data_structure, base_data_structure)
    ports = __jmdl_load_ports(jmdl, data_structure, base_data_structure)
    subsystems = __jmdl_load_subsystems(jmdl, data_structure, base_data_structure)

    components = components + ports + subsystems

    __jmdl_load_graph(jmdl, components, data_structure)
    return data_structure


def __load_components(
    jmdl: JmdlModel, data_structure: DataStructure, base_data_structure: DataStructure
) -> list[Component]:
    components: list[Component] = []

    for block in jmdl.root.blocks:
        create = Components.CREATION_FUNCTION_DICT.get(block.block_class, None)
        if create is not None:
            gdf_component = create(block, base_data_structure.get_valid_id())
            data_structure.add_component(gdf_component)
            components.append(gdf_component)

    return components


def __jmdl_load_subsystems(
    jmdl: JmdlModel, data_structure: DataStructure, base_data_structure: DataStructure
) -> list[Component]:
    """Load the super blocks from a JMDL object into the Generic Data Model.

    :param jmdl: The JMDL object
    :type jmdl: JMDLImport
    :return: The list of subsystems
    :rtype: list[Component]
    """
    subsystems: list[Component] = []
    for super_block in jmdl.root.super_blocks:
        # create an empty subsystem and add it to the data structure
        # this ensures that adding components to the subsystem does not invalidate the id generation
        next_id = base_data_structure.get_valid_id()
        gdf_subsystem = Subsystem(next_id, super_block.name, None)
        data_structure.add_component(gdf_subsystem)

        jmdl_import = JmdlModel(
            "",
            False,
            Data(
                "",
                DataType.GROUP,
                [Data("", DataType.FLOAT64, [], 0.0, None, "frequency")],
            ),
            super_block,
            [],
        )

        import_jmdl(jmdl_import, base_data_structure=base_data_structure, graph=gdf_subsystem.graph)

        subsystems.append(gdf_subsystem)
    return subsystems


def __jmdl_load_ports(
    jmdl: JmdlModel, data_structure: DataStructure, base_data_structure: DataStructure
) -> list[GdfPort]:
    """Load the ports from a JMDL object into the Generic Data Model.

    :param jmdl: The JMDL object
    :type jmdl: JMDLImport
    :return: The list of ports
    :rtype: list[Port]
    """
    ports: list[GdfPort] = []
    for port in jmdl.root.ports:
        gdf_port = GdfPort(base_data_structure.get_valid_id(), port.name, None, 0)
        data_structure.add_component(gdf_port)
        ports.append(gdf_port)
    return ports


def __jmdl_load_graph(jmdl: JmdlModel, elements: list[Any], data_structure: DataStructure) -> None:
    """Loads the components and their connections from a JMDL object into the Generic Data Model Networkx graph.

    :param jmdl: The JMDL object
    :type jmdl: JMDLImport
    :param elements: The list of elements
    :type elements: list[Any]
    :return: The graph
    :rtype: Graph
    """

    # {block name}.{port name} -> (block, port name)
    ports: dict[str, tuple[Block | Root | Port, str]] = {}
    for block in jmdl.root.blocks + jmdl.root.super_blocks:
        for port in block.ports:
            ports[f"{block.name}.{port.name}"] = (block, port.name)
    for port in jmdl.root.ports:
        ports[f".{port.name}"] = (port, port.name)

    for connection in jmdl.root.connections:
        if connection.start not in ports or connection.end not in ports:
            raise ValueError(f"Connection {connection.start} -> {connection.end} is invalid")
        start_block, start_port_name = ports[connection.start]
        end_block, end_port_name = ports[connection.end]
        start_element = next(
            (e for e in elements if e.name == start_block.name),
            None,
        )
        end_element = next(
            (e for e in elements if e.name == end_block.name),
            None,
        )
        if start_element is None or end_element is None:
            raise ValueError(f"Connection {connection.start} -> {connection.end} is invalid")
        data_structure.add_connection(start_element, end_element, start_port_name, end_port_name)
