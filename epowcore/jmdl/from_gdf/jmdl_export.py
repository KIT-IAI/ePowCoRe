from typing import Counter

from epowcore.gdf import DataStructure, Bus, Load
from epowcore.gdf.component import Component
from epowcore.gdf.exciters.exciter import Exciter
from epowcore.gdf.generators.generator import Generator
from epowcore.gdf.governors.governor import Governor
from epowcore.gdf.power_system_stabilizers import PowerSystemStabilizer
from epowcore.gdf.tline import TLine
from epowcore.gdf.pv_system import PVSystem
from epowcore.gdf.transformers import Transformer
from epowcore.gdf.external_grid import ExternalGrid
from epowcore.gdf.port import Port as GdfPort
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.switch import Switch
from epowcore.gdf.subsystem import Subsystem
from epowcore.gdf.voltage_source import VoltageSource
from epowcore.generic.tools.debugging import visualize_neighborhood_and_raise_error
from epowcore.jmdl.from_gdf import block_builder
from epowcore.jmdl.from_gdf.transform import transform
from epowcore.jmdl.utils import clean
from epowcore.jmdl.jmdl_model import JmdlModel, Data, DataType, PortInternals, Tag, Root
from epowcore.jmdl.jmdl_model import (
    Block,
    BorderLayout,
    CableLayout,
    Connection,
    Layout,
    Port,
)

ALLOWED_COMPONENT_CONNECTION = [
    TLine,
    Transformer,
    Switch,
    Shunt,
    Generator,
    PVSystem,
    VoltageSource,
    ExternalGrid,
    Load,
    Exciter,
    Governor,
    PowerSystemStabilizer,
]


def export_jmdl(
    data_struct: DataStructure,
    version: str = "0.6",
    geo_mode: bool = False,
    base_mva: float = 100,
    bg_width: float = 0,
    bg_height: float = 0,
    bg_image: str = "",
    minified: bool = False,
) -> JmdlModel:
    """Generates a JMDL file from a data structure

    :param data_struct: The data structure to generate the JMDL file from
    :return: The JMDL file as a string
    """

    data_entries = [
        Data("", DataType.FLOAT64, [], base_mva, None, "baseMVA"),
        Data("", DataType.INT64, [], data_struct.base_frequency, None, "frequency"),
        Data("", DataType.STRING, [], "2", None, "mpcVersion"),
    ]
    data = Data("", DataType.GROUP, data_entries, None, None, "data")

    name_collision = len(data_struct.graph.nodes) != len(
        set(x.name for x in data_struct.graph.nodes)
    )
    blocks = __get_blocks(data_struct, base_mva, name_collision)

    root = Root(
        "/",
        [],
        "SuperBlock",
        blocks=[x for x in blocks.values() if isinstance(x, Block)],
        super_blocks=[x for x in blocks.values() if isinstance(x, Root)],
        connections=__get_connections(data_struct, blocks)
        + __get_super_block_connections(data_struct, blocks),
        comment="",
        url="",
        tags=["Group"],
        data=Data(
            "",
            DataType.GROUP,
            [
                Data("", DataType.FLOAT64, [], bg_width, None, "backgroundWidth"),
                Data("", DataType.FLOAT64, [], bg_height, None, "backgroundHeight"),
                Data("", DataType.STRING, [], bg_image, None, "backgroundImage"),
            ],
            None,
            None,
            "data",
        ),
        layout=Layout(
            center=[0, 0],
            size=[100, 60],
        ),
    )
    tags: list[Tag] = []

    return JmdlModel(version, geo_mode, data, root, tags)


def __get_blocks(
    data_struct: DataStructure, base_mva: float, name_collision: bool
) -> dict[int, Block | Root]:
    components = block_builder.get_components(data_struct, base_mva, name_collision)
    super_blocks = __get_super_blocks(data_struct, name_collision)

    return components | super_blocks


def __get_super_blocks(data_structure: DataStructure, name_collision: bool) -> dict[int, Root]:
    """Creates a generic super block out of a list of blocks.

    :param data_structure: Data structure
    :param blocks: List of blocks
    :type blocks: list[Block]
    """

    super_blocks: dict[int, Root] = {}
    for subsystem in data_structure.type_list(Subsystem):
        fake_ds = DataStructure(
            base_frequency=data_structure.base_frequency,
            graph=subsystem.graph,
            version=data_structure.version,
        )
        fake_ds = transform(fake_ds)
        blocks = __get_blocks(
            data_struct=fake_ds,
            base_mva=data_structure.base_frequency,
            name_collision=name_collision,
        )
        __add_internal_to_ports(blocks)
        connections = __get_connections(fake_ds, blocks)
        ports: list[Port] = block_builder.get_ports(data_structure, subsystem)
        for port in ports:
            port.internal = PortInternals()
        super_blocks[subsystem.uid] = Root(
            name=clean(subsystem.name),
            ports=ports,
            _type="SuperBlock",
            blocks=[x for x in blocks.values() if isinstance(x, Block)],
            super_blocks=[x for x in blocks.values() if isinstance(x, Root)],
            connections=connections,
            comment="",
            url="",
            tags=[],
            data=Data(
                "",
                DataType.GROUP,
                [
                    Data(
                        "",
                        DataType.GROUP,
                        [
                            Data("", DataType.FLOAT64, [], 0, None, "backgroundWidth"),
                            Data(
                                "",
                                DataType.FLOAT64,
                                [],
                                0,
                                None,
                                "backgroundHeight",
                            ),
                            Data("", DataType.IMAGE, [], "", None, "backgroundImage"),
                        ],
                        None,
                        None,
                        "SuperBlock",
                    ),
                    block_builder.get_geo_data(subsystem),
                ],
                None,
                None,
                "data",
            ),
            layout=Layout(
                center=[0, 0],
                size=[100, 60],
            ),
        )
    return super_blocks


def __add_internal_to_ports(blocks: dict[int, Block | Root]) -> None:
    """Adds the internal ports of a block to the list of ports."""
    for block in blocks.values():
        if isinstance(block, Root):
            for port in block.ports:
                port.internal = PortInternals()
        else:
            for port in block.ports:
                port.internal = PortInternals()


def __get_connections(
    data_struct: DataStructure, blocks: dict[int, Block | Root]
) -> list[Connection]:
    """Extract the connections from the data structure to JMDL Connections

    :param data_struct: Data structure
    :type data_struct: DataStructure
    :param blocks: Extracted blocks
    :type blocks: list[Block]
    :return: Connections as JMDL Connections
    :rtype: list[Connection]
    """
    connections = []
    elements: list[Component] = data_struct.type_list(ALLOWED_COMPONENT_CONNECTION)
    connection_counter = {branch.uid: 0 for branch in elements}
    for from_component, to_component in data_struct.graph.edges:
        # TODO: maybe a whitelist is the better option here, because JMDL has a very limited library
        if not __is_valid_connection(from_component, to_component):
            continue
        from_block = blocks.get(from_component.uid)
        to_block = blocks.get(to_component.uid)

        for component, block in [
            (from_component, from_block),
            (to_component, to_block),
        ]:
            if not __is_valid_block(component, block):
                raise ValueError(
                    f"Block not found: <{type(component).__name__}> {component.name} ({component.uid})"
                )

        from_port = None
        to_port = None

        # Sort Bus to to-Port
        if isinstance(from_component, Bus):
            # Swap from and to (Bus is always to)
            from_block, to_block = to_block, from_block
            from_component, to_component = to_component, from_component
            if isinstance(from_component, Bus):
                raise ValueError("Two buses can not be directly connected!")

        # Identify relevant ports
        if isinstance(from_component, GdfPort):
            from_block, from_port = __handle_gdf_port(from_component)
        if from_block is None:
            raise ValueError(
                f"Block not found: <{type(from_component).__name__}>"
                + f" {from_component.name} ({from_component.uid})"
            )
        if isinstance(from_component, (Generator, VoltageSource, PVSystem, ExternalGrid)):
            from_port = __try_get_port(from_component, from_block, "powerOut", connection_counter)
        elif isinstance(from_component, (Load, Shunt)):
            from_port = __try_get_port(from_component, from_block, "powerIn", connection_counter)
        elif isinstance(from_component, (TLine, Transformer, Switch)):
            comp_id = from_component.uid
            if connection_counter[comp_id] > 2:
                # Insert BusBar
                visualize_neighborhood_and_raise_error(
                    data_struct,
                    from_component,
                    f"Component {from_component} has more than 2 connections",
                )

            from_port = __get_port_from_block(
                from_block, "from" if connection_counter[comp_id] == 0 else "to"
            )
            connection_counter[comp_id] += 1
        elif not isinstance(from_component, (Bus, GdfPort)):
            raise ValueError(
                f"Unknown component type: {type(from_component).__name__} ({from_component.name})"
            )

        to_port = __get_to_port(from_component, to_block) if to_block else None

        __handle_connection_errors(from_component, to_component, from_port, to_port, data_struct)

        border_layout = (
            __border_layout(from_component)
            if connection_counter.get(from_component.uid, 0) == 1
            else BorderLayout()
        )
        connections.append(
            Connection(
                f"{clean(from_block.name)}.{from_port.name}",  # type: ignore
                f"{clean(to_block.name)}.{to_port.name}",  # type: ignore
                border_layout,
            )
        )
    return connections


def __get_super_block_connections(
    data_structure: DataStructure, blocks: dict[int, Block | Root]
) -> list[Connection]:
    """Determines the connections connecting super blocks with other components."""
    connection_counter: Counter = Counter()
    connections: list[Connection] = []
    for subsystem in data_structure.type_list(Subsystem):
        subsystem_ports = [n for n in subsystem.graph.nodes if isinstance(n, GdfPort)]
        for _, other, _ in data_structure.graph.edges.data(subsystem):
            for gdf_port in [p for p in subsystem_ports if p.connection_component == other.uid]:
                connection_counter.update([other.uid])
                check = ""
                if connection_counter[other.uid] == 1:
                    check = "to"
                elif connection_counter[other.uid] == 2:
                    check = "from"
                other_port = next(
                    (port for port in blocks[other.uid].ports if check in port.name),
                    blocks[other.uid].ports[-1],
                )

                connections.append(
                    Connection(
                        f"{clean(subsystem.name)}.{gdf_port.name}",
                        f"{clean(blocks[other.uid].name)}.{other_port.name}",
                        BorderLayout(),
                    )
                )
                subsystem_ports.remove(gdf_port)
    return connections


def __is_valid_connection(from_component: Component, to_component: Component) -> bool:
    return not isinstance(
        from_component, (Exciter, Governor, PowerSystemStabilizer, Subsystem)
    ) and not isinstance(to_component, (Exciter, Governor, PowerSystemStabilizer, Subsystem))


def __is_valid_block(component: Component, block: Block | Root | None) -> bool:
    """Checks if a block is valid for a component, raises an error if not."""
    return not (block is None and not isinstance(component, GdfPort))


def __handle_gdf_port(component: GdfPort) -> tuple[Block, Port]:
    """Handles a GdfPort, creates a block and a port for it."""
    block = Block("", [], "", "", "", "", [], Data(), Layout())
    port = Port(
        "ConservingPort",
        component.name,
        CableLayout(),
        None,
    )
    return block, port


def __get_port_from_block(block: Block | Root, port_name: str) -> Port | None:
    return next((port for port in block.ports if port.name == port_name), None)


def __get_to_port(component: Component, to_block: Block | Root) -> Port | None:
    to_port = next(
        filter(
            lambda x: x.name.startswith(
                f"to_{block_builder.get_port_component_name(component)}" + f"{component.uid}"
            ),
            to_block.ports,  # type: ignore
        ),
        None,
    )
    return to_port


def __try_get_port(
    component: Component,
    block: Block | Root,
    port_name: str,
    counter: dict,
) -> Port | None:
    """Tries to get a port from a block, returns None if not found."""
    port = next((port for port in block.ports if port.name == port_name), None)
    if port is None:
        raise ValueError(f"Port {port_name} not found in block {block.name}")
    counter[component.uid] += 1
    if counter[component.uid] > 1:
        raise ValueError(f"More than one port {port_name} in block {block.name}")
    return port


def __handle_connection_errors(
    from_component: Component,
    to_component: Component,
    from_port: Port | None,
    to_port: Port | None,
    data_struct: DataStructure,
) -> None:
    if not isinstance(to_component, (TLine, Switch, Bus)):
        # Should not happen, bus bars should separate the components
        visualize_neighborhood_and_raise_error(
            data_struct,
            to_component if from_component is None else from_component,
            f"Connection to non bus bar component: {to_component}",
        )
    if from_port is None or to_port is None:
        visualize_neighborhood_and_raise_error(
            data_struct,
            to_component if from_component is None else from_component,
            f"Could not find port for component {from_component.name}",
        )


def __border_layout(component: Component) -> BorderLayout:
    if not isinstance(component.coords, list):
        return BorderLayout()
    points: list[float] = [0.0 for _ in range(2 * (len(component.coords) - 1))]
    geo_points: list[float] = [a for b in component.coords[1:] for a in b]
    return BorderLayout(points=points, geo_points=geo_points)
