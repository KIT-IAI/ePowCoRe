from typing import Any

from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.component import Component
from epowcore.gdf.bus import Bus
from epowcore.gdf.generators.generator import Generator
from epowcore.gdf.load import Load
from epowcore.gdf.external_grid import ExternalGrid
from epowcore.gdf.pv_system import PVSystem
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.subsystem import Subsystem
from epowcore.gdf.switch import Switch
from epowcore.gdf.transformers.transformer import Transformer
from epowcore.gdf.tline import TLine
from epowcore.gdf.port import Port as GdfPort
from epowcore.gdf.voltage_source import VoltageSource

from epowcore.jmdl.from_gdf.components.bus import create_bus_block
from epowcore.jmdl.from_gdf.components.external_grid import create_external_grid_block
from epowcore.jmdl.from_gdf.components.generator import (
    create_generator_block,
    create_pv_generator_block,
)
from epowcore.jmdl.from_gdf.components.line import create_line_block
from epowcore.jmdl.from_gdf.components.load import create_load_block
from epowcore.jmdl.from_gdf.components.shunt import create_shunt_block
from epowcore.jmdl.from_gdf.components.switch import create_switch_block
from epowcore.jmdl.from_gdf.components.transformer import create_transformer_block
from epowcore.jmdl.from_gdf.components.voltage_source import create_vsource_block

from epowcore.jmdl.jmdl_model import (
    Data,
    DataType,
    Block,
    CableLayout,
    Port,
)

PORT_COMPONENT_NAMES = {
    Bus: "Bus",
    TLine: "Line",
    Transformer: "Transformer",
    (Generator, VoltageSource, PVSystem): "Generator",
    Load: "Load",
    Shunt: "Shunt",
    Switch: "Switch",
    (GdfPort, Subsystem): "Port",
    ExternalGrid: "ExternalGrid",
}


def get_components(
    core_model: CoreModel, base_mva: float, name_collision: bool
) -> dict[int, Block]:
    components = {}
    for component in core_model.graph.nodes:
        ports = get_ports(core_model, component)
        geo_data = get_geo_data(component)

        if isinstance(component, ExternalGrid):
            components[component.uid] = create_external_grid_block(
                component, ports, geo_data, name_collision
            )
        elif isinstance(component, Switch):
            components[component.uid] = create_switch_block(
                component, ports, geo_data, name_collision
            )
        elif isinstance(component, Shunt):
            components[component.uid] = create_shunt_block(
                component, ports, geo_data, name_collision
            )
        elif isinstance(component, Bus):
            components[component.uid] = create_bus_block(
                component, ports, geo_data, name_collision
            )
        elif isinstance(component, Generator):
            components[component.uid] = create_generator_block(
                component, ports, geo_data, name_collision
            )
        elif isinstance(component, VoltageSource):
            components[component.uid] = create_vsource_block(
                component, ports, geo_data, name_collision
            )
        elif isinstance(component, PVSystem):
            components[component.uid] = create_pv_generator_block(
                component, ports, geo_data, name_collision
            )
        elif isinstance(component, TLine):
            components[component.uid] = create_line_block(
                component,
                core_model.graph,
                base_mva,
                ports,
                geo_data,
                name_collision,
            )
        elif isinstance(component, Transformer):
            components[component.uid] = create_transformer_block(
                component, base_mva, ports, geo_data, name_collision
            )
        elif isinstance(component, Load):
            components[component.uid] = create_load_block(
                component, ports, geo_data, name_collision
            )

    return components

def get_ports(core_model: CoreModel, comp: Component) -> list[Port]:
    ports: list[Port] = []

    compi = core_model.get_component_by_id(comp.uid)[0]
    if compi is None:
        raise ValueError(
            f"Component not found: <{type(comp).__name__}> {comp.name} ({comp.uid})"
        )
    if isinstance(comp, Bus):
        for neighbor in list(core_model.graph.neighbors(comp)):
            # if neighbor.uid in self._components or isinstance(neighbor, GdfPort):
            conn_uid = neighbor.uid
            if isinstance(neighbor, Subsystem):
                conn_uid = comp.uid
            ports.append(
                Port(
                    "ConservingPort",
                    f"to_{get_port_component_name(neighbor)}{conn_uid}",
                    CableLayout(),
                    None,
                )
            )
    if isinstance(comp, (Generator, VoltageSource, PVSystem, ExternalGrid)):
        ports.append(Port("ConservingPort", "powerOut", CableLayout()))
    elif isinstance(comp, Load):
        ports.append(Port("ConservingPort", "powerIn", CableLayout()))
    elif isinstance(comp, Shunt):
        ports.append(Port("ConservingPort", "powerIn", CableLayout()))
    elif isinstance(comp, (TLine, Transformer, Switch)):
        ports.append(Port("ConservingPort", "from", CableLayout()))
        ports.append(Port("ConservingPort", "to", CableLayout()))
    elif isinstance(comp, Subsystem):
        for gdfport in [x for x in comp.graph.nodes if isinstance(x, GdfPort)]:
            ports.append(Port("ConservingPort", gdfport.name, CableLayout(), None))
    for i, port in enumerate(ports):
        port.layout.borderPos = float(i / len(ports))
    return ports

def get_geo_data(
    component: Component,
    label_text: str = "",
    label_text_color: str = "",
    geographic_shape: str = "",
    line_color: str = "",
    line_thickness: str = "",
    fill_color: str = "",
) -> Data:
    """Creates a data entry geoData with the default values

    :return: GeoData as JMDL data
    :rtype: Data
    """
    coordinates = ""
    if component.coords is not None:
        if isinstance(component.coords, list):
            # Assign first coordinate as component center
            coordinates = f"{component.coords[0][0]},{component.coords[0][1]},0.0"
        else:
            coordinates = f"{component.coords[0]},{component.coords[1]},0.0"
    return Data(
        description="Geographic Data and Shape of the real world Object represented by this block.",
        data_type=DataType.GROUP,
        entries=[
            Data(
                "A meaningful label text.",
                DataType.STRING,
                [],
                label_text,
                None,
                "label",
            ),
            Data(
                "Label text color.",
                DataType.STRING,
                [],
                label_text_color,
                None,
                "labelColor",
            ),
            Data(
                "Coordinates of the geographic center. Please use '<lat>,<lon>,<alt>'",
                DataType.STRING,
                [],
                coordinates,
                None,
                "center",
            ),
            Data(
                "Geographic shape.",
                DataType.STRING,
                [],
                geographic_shape,
                None,
                "path",
            ),
            Data(
                "Color of the path line.",
                DataType.STRING,
                [],
                line_color,
                None,
                "lineColor",
            ),
            Data(
                "Thickness of the path line.",
                DataType.STRING,
                [],
                line_thickness,
                None,
                "lineThickness",
            ),
            Data(
                "The enclosed area's fill color, provided the path is closed.",
                DataType.STRING,
                [],
                fill_color,
                None,
                "fillColor",
            ),
        ],
        value=None,
        enum_class=None,
        name="geoData",
    )

def get_port_component_name(component: Any) -> str:
    """Get the name for the port naming by component type

    :param component: Component
    :type component: Any
    :return: Name for the port
    :rtype: str
    """
    for types, name in PORT_COMPONENT_NAMES.items():
        if isinstance(component, types):  # type: ignore
            return name
    raise ValueError("Unknown component type")
