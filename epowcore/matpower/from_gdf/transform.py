import copy

from epowcore.gdf import DataStructure
from epowcore.gdf.bus import Bus
from epowcore.gdf.extended_ward import ExtendedWard
from epowcore.gdf.external_grid import ExternalGrid
from epowcore.gdf.generators.generator import Generator
from epowcore.gdf.impedance import Impedance
from epowcore.gdf.load import Load
from epowcore.gdf.port import Port
from epowcore.gdf.pv_system import PVSystem
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.subsystem import Subsystem
from epowcore.gdf.switch import Switch
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.voltage_source import VoltageSource
from epowcore.gdf.ward import Ward
from epowcore.generic.component_graph import ComponentGraph
from epowcore.generic.constants import Platform
from epowcore.generic.logger import Logger
from epowcore.generic.manipulation.merge_components import merge_components

WHITE_LIST = (
    Bus,
    ExternalGrid,
    Generator,
    TLine,
    PVSystem,
    Load,
    Shunt,
    Switch,
    TwoWindingTransformer,
    VoltageSource,
    Subsystem,
    Port,
)


def transform(data_structure: DataStructure) -> DataStructure:
    """Transform the generic model to make it compatible to Matpower."""
    data_struct = copy.deepcopy(data_structure)

    nodes = list(data_struct.graph.nodes)
    for n in nodes:
        # remove buses without type -> isolated
        if isinstance(n, Bus) and n.lf_bus_type is None:
            Logger.log_to_selected(f"Removing bus without type: {n.name}")
            data_struct.graph.remove_node(n)

    nodes = list(data_struct.graph.nodes)
    for n in nodes:
        # remove nodes without neighbors
        if len(list(data_struct.graph.neighbors(n))) == 0:
            Logger.log_to_selected(f"Removing outlier node: {n.name}")
            data_struct.graph.remove_node(n)

    # Replace extended Ward equivalents with loads, shunts, impedances and voltage sources
    ext_wards = [n for n in data_struct.graph.nodes if isinstance(n, ExtendedWard)]
    for ext_ward in ext_wards:
        ext_ward.replace_with_load_shunt_vsource(data_struct)

    # Replace Ward equivalents with loads and shunts
    # Order is important because ExtendedWard is also a Ward!
    wards = [n for n in data_struct.graph.nodes if isinstance(n, Ward)]
    for ward in wards:
        ward.replace_with_load_and_shunt(data_struct)

    # Replace impedances with lines
    impedances = [n for n in data_struct.graph.nodes if isinstance(n, Impedance)]
    for impedance in impedances:
        impedance.replace_with_line(data_struct, Platform.MATPOWER)

    three_winding_transformers = data_struct.type_list(ThreeWindingTransformer)

    for three_winding_transformer in three_winding_transformers:
        Logger.log_to_selected(
            f"Replacing three-winding transformer: {three_winding_transformer.name}"
        )
        three_winding_transformer.replace_with_two_winding_transformers(data_struct)

    # Merge neighbouring buses
    for bus in data_struct.type_list(Bus):
        if data_struct.graph.has_node(bus):
            for neighbour in list(data_struct.graph.neighbors(bus)):
                if isinstance(neighbour, Bus):
                    merge_components(data_struct, bus, neighbour)

    _remove_not_supported(data_struct.graph)

    return data_struct


def _remove_not_supported(graph: ComponentGraph) -> None:
    """Remove all nodes that are not supported by JMDL.

    :param graph: The graph to remove the unsupported nodes from.
    :type graph: ComponentGraph
    """
    components = list(graph.nodes)
    for c in components:
        if not isinstance(c, WHITE_LIST):
            Logger.log_to_selected(f"Removing unsupported node: {c.name}")
            graph.remove_node(c)
        elif isinstance(c, Subsystem):
            _remove_not_supported(c.graph)
            # If only ports are left in the Subsystem, remove
            if len(c.graph.nodes) == len(
                [n for n in c.graph.nodes if isinstance(n, Port)]
            ):
                Logger.log_to_selected(f"Removing empty subsystem: {c.name}")
                graph.remove_node(c)
