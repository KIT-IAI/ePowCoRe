from typing import Any

import epowcore.jmdl.to_gdf.components as Components
from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.port import Port as GdfPort
from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.component_graph import ComponentGraph
from epowcore.jmdl.jmdl_model import Block, Data, DataType, JmdlModel, Port, Root


def import_jmdl(
    jmdl: JmdlModel,
    base_core_model: CoreModel | None = None,
    graph: ComponentGraph | None = None,
) -> CoreModel:
    """Imports a JMDLModel and converts it to a GDF CoreModel.

    :param jmdl: The JMDL object
    :type jmdl: JMDLImport
    :param base_core_model: Required for recursive calls to keep track of IDs.
    :type base_core_model: CoreModel | None
    :param graph: Required for recursive calls to add components to correct graph.
    :type graph: ComponentGraph | None
    """
    if graph is None:
        core_model = CoreModel(base_frequency=jmdl.base_frequency, base_mva=jmdl.base_mva)
    else:
        core_model = CoreModel(
            base_frequency=jmdl.base_frequency, base_mva=jmdl.base_mva, graph=graph
        )

    if base_core_model is None:
        base_core_model = core_model

    components: list[Component] = __load_components(jmdl, core_model, base_core_model)
    ports = __jmdl_load_ports(jmdl, core_model, base_core_model)
    subsystems = __jmdl_load_subsystems(jmdl, core_model, base_core_model)

    components = components + ports + subsystems

    __jmdl_load_graph(jmdl, components, core_model)
    return core_model


def __load_components(
    jmdl: JmdlModel, core_model: CoreModel, base_core_model: CoreModel
) -> list[Component]:
    components: list[Component] = []

    for block in jmdl.root.blocks:
        create = Components.CREATION_FUNCTION_DICT.get(block.block_class, None)
        if create is not None:
            gdf_component = create(block, base_core_model.get_valid_id())
            core_model.add_component(gdf_component)
            components.append(gdf_component)

    return components


def __jmdl_load_subsystems(
    jmdl: JmdlModel, core_model: CoreModel, base_core_model: CoreModel
) -> list[Component]:
    """Load the super blocks from a JMDL object into the Generic Data Model.

    :param jmdl: The JMDL object
    :type jmdl: JMDLImport
    :return: The list of subsystems
    :rtype: list[Component]
    """
    subsystems: list[Component] = []
    for super_block in jmdl.root.super_blocks:
        # create an empty subsystem and add it to the core model
        # this ensures that adding components to the subsystem does not invalidate the id generation
        next_id = base_core_model.get_valid_id()
        gdf_subsystem = Subsystem(next_id, super_block.name, None)
        core_model.add_component(gdf_subsystem)

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

        import_jmdl(jmdl_import, base_core_model=base_core_model, graph=gdf_subsystem.graph)

        subsystems.append(gdf_subsystem)
    return subsystems


def __jmdl_load_ports(
    jmdl: JmdlModel, core_model: CoreModel, base_core_model: CoreModel
) -> list[GdfPort]:
    """Load the ports from a JMDL object into the Generic Data Model.

    :param jmdl: The JMDL object
    :type jmdl: JMDLImport
    :return: The list of ports
    :rtype: list[Port]
    """
    ports: list[GdfPort] = []
    for port in jmdl.root.ports:
        gdf_port = GdfPort(base_core_model.get_valid_id(), port.name, None, 0)
        core_model.add_component(gdf_port)
        ports.append(gdf_port)
    return ports


def __jmdl_load_graph(jmdl: JmdlModel, elements: list[Any], core_model: CoreModel) -> None:
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
        core_model.add_connection(start_element, end_element, start_port_name, end_port_name)
