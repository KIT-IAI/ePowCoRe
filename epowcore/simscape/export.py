from datetime import datetime
import pathlib
import time

import matlab.engine

from epowcore.gdf.bus import Bus
from epowcore.gdf.common_impedance import CommonImpedance
from epowcore.gdf.exciters.sexs import SEXS
from epowcore.gdf.generators.static_generator import StaticGenerator
from epowcore.gdf.governors.gast import GAST
from epowcore.gdf.governors.hygov import HYGOV
from epowcore.gdf.load import Load
from epowcore.gdf.component import Component
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.exciters.ieee_st1a import IEEEST1A
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.governors.ieee_g1 import IEEEG1
from epowcore.gdf.port import Port
from epowcore.gdf.power_system_stabilizers.ieee_pss2a import IEEEPSS2A
from epowcore.gdf.subsystem import Subsystem
from epowcore.gdf.power_system_stabilizers import IEEEPSS1A
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.generic.logger import Logger
from epowcore.simscape.components.bus import create_bus
from epowcore.simscape.components.gast import create_gast
from epowcore.simscape.components.generator import create_generator
from epowcore.simscape.components.hygov import create_hygov
from epowcore.simscape.components.ieee_g1 import create_ieee_g1
from epowcore.simscape.components.common_impedance import create_common_impedance
from epowcore.simscape.components.ieee_pss2a import create_ieee_pss2a
from epowcore.simscape.components.in_outport import create_inport
from epowcore.simscape.components.load import create_load
from epowcore.simscape.components.powergui import create_powergui
from epowcore.simscape.components.sexs import create_sexs
from epowcore.simscape.components.static_gen import create_static_generator
from epowcore.simscape.components.tline import create_tline
from epowcore.simscape.components.ieee_st1a import create_ieee_st1a
from epowcore.simscape.components.ieee_pss1a import create_ieee_pss1a
from epowcore.simscape.components.two_winding_transformer import create_tw_trans
from epowcore.simscape.components.three_winding_transformer import create_thw_trans
from epowcore.simscape.components.vi_measurement import create_vi_measurement
from epowcore.simscape.connector import connect
from epowcore.simscape.layouter import layout_model
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape import simscape_graph_transformer
from epowcore.simscape.subsystem_helper import (
    get_subsystem_template,
    insert_subsystem,
    insert_subsystem_template,
)
from epowcore.simscape.tools import get_position, set_position


PATH = pathlib.Path(__file__).parent.resolve()


def export(
    data_structure: DataStructure,
    model_name: str,
    engine: matlab.engine.MatlabEngine | None = None,
    is_subsystem: bool = False,
) -> None:
    """Take the data structure, go through its components and create a Simscape model accordingly."""
    if engine is None:
        eng = matlab.engine.start_matlab()
        if not isinstance(eng, matlab.engine.MatlabEngine):
            raise ValueError("Failed to start matlab engine")
    else:
        eng = engine

    eng.addpath(str(PATH / "lib"), nargout=0)

    Logger.log_to_selected(f"Start export to simscape model '{model_name}'")
    eng.new_system(model_name)  # type: ignore

    start = time.perf_counter()
    created_components = __create_components(eng, data_structure, model_name)
    print(f"component creation: {time.perf_counter() - start:.1f}s")

    print(f"{datetime.now().timestamp()} Layouting model")
    layout_model(eng, data_structure.graph.get_internal_graph(copy=False), created_components)

    print(f"{datetime.now().timestamp()} Add load flow buses")
    # After all components are created and placed, add the load flow buses
    for bus in data_structure.type_list(Bus):
        vim = created_components[bus]
        sbus = create_bus(eng, bus, data_structure, model_name)
        x, y, _, _ = get_position(eng, vim)
        set_position(eng, sbus, x + 50, y)
        connect(eng, model_name, vim, "RConn", sbus, "")

    print(f"{datetime.now().timestamp()} Adding edge data")
    simscape_graph_transformer.add_known_edge_data(data_structure.graph, created_components)

    print(f"{datetime.now().timestamp()} Connecting components")
    __connect_components(eng, data_structure, model_name, created_components)

    if not is_subsystem:
        create_powergui(eng, model_name)
    print(f"{datetime.now().timestamp()} Saving model")
    eng.save_system(model_name)  # type: ignore
    print(f"{datetime.now().timestamp()} Saved model")


def __create_components(
    eng: matlab.engine.MatlabEngine, data_structure: DataStructure, model_name: str
) -> dict[Component, SimscapeBlock]:
    """Create all components in the model and return a dict with the created components.

    :param eng: MATLAB engine
    :param data_structure: GDF Data structure
    :param model_name: Name of the model
    :return: Mapping from the GDF components to the created Simscape blocks
    """
    created_components: dict[Component, SimscapeBlock] = {}

    component: Component
    for component in data_structure.type_list(Bus):
        # We use VI measurements as bus replacements here because it is way easier to create
        # the component connections with these. We just need to make sure to add load flow buses
        # later in the export process.
        print(f"{datetime.now().timestamp()} Creating VI measurement for bus {component.name}")
        created_components[component] = create_vi_measurement(eng, f"VIM {component.name}", model_name)[0]

    for component in data_structure.type_list(Load):
        print(f"{datetime.now().timestamp()} Creating load {component.name}")
        created_components[component] = create_load(eng, component, data_structure, model_name)
    for component in data_structure.type_list(SynchronousMachine):
        print(f"{datetime.now().timestamp()} Creating generator {component.name}")
        created_components[component] = create_generator(eng, component, data_structure, model_name)
    for component in data_structure.type_list(StaticGenerator):
        print(f"{datetime.now().timestamp()} Creating static generator {component.name}")
        created_components[component] = create_static_generator(eng, component, data_structure, model_name)

    for component in data_structure.type_list(TLine):
        print(f"{datetime.now().timestamp()} Creating transmission line {component.name}")
        created_components[component] = create_tline(eng, component, data_structure, model_name)
    for component in data_structure.type_list(TwoWindingTransformer):
        print(f"{datetime.now().timestamp()} Creating two winding transformer {component.name}")
        created_components[component] = create_tw_trans(eng, component, data_structure, model_name)
    for component in data_structure.type_list(ThreeWindingTransformer):
        print(f"{datetime.now().timestamp()} Creating three winding transformer {component.name}")
        created_components[component] = create_thw_trans(eng, component, data_structure, model_name)
    for component in data_structure.type_list(CommonImpedance):
        created_components[component] = create_common_impedance(
            eng, component, data_structure, model_name
        )

    # Governors
    for component in data_structure.type_list(IEEEG1):
        created_components[component] = create_ieee_g1(eng, component, model_name)
    for component in data_structure.type_list(GAST):
        created_components[component] = create_gast(eng, component, model_name)
    for component in data_structure.type_list(HYGOV):
        created_components[component] = create_hygov(eng, component, model_name)
    # Exciters
    for component in data_structure.type_list(IEEEST1A):
        created_components[component] = create_ieee_st1a(eng, component, model_name)
    for component in data_structure.type_list(SEXS):
        created_components[component] = create_sexs(eng, component, model_name)
    # PSS
    for component in data_structure.type_list(IEEEPSS1A):
        created_components[component] = create_ieee_pss1a(eng, component, model_name)
    for component in data_structure.type_list(IEEEPSS2A):
        created_components[component] = create_ieee_pss2a(eng, component, model_name)

    for component in data_structure.type_list(Port):
        # TODO:Identify whether the port is an inport or an outport
        created_components[component] = create_inport(eng, component, model_name)

    for subsystem in data_structure.type_list(Subsystem):
        print(f"{datetime.now().timestamp()} Creating subsystem {subsystem.name}")
        # check for available subsystem templates
        subsystem_template = get_subsystem_template(subsystem)

        if subsystem_template is None:
            # No template available -> Create simple subsystem
            created_components[subsystem] = insert_subsystem(
                eng, subsystem, model_name, data_structure.base_frequency
            )
        else:
            # Use templated subsystem with additional components
            created_subsystem = insert_subsystem_template(
                eng,
                model_name,
                subsystem,
                subsystem_template,
            )
            if created_subsystem is not None:
                created_components[subsystem] = created_subsystem

    return created_components


def __connect_components(
    eng: matlab.engine.MatlabEngine,
    data_structure: DataStructure,
    model_name: str,
    created_components: dict[Component, SimscapeBlock],
) -> None:
    """Connect the components according to the graph."""
    for left, right, data in data_structure.graph.edges.data():
        if left not in created_components or right not in created_components:
            print(f"Could not connect {left} to {right} as one of them is not created yet.")
            continue

        # Special case for subsystem as their simulink type has to be read from a dict
        left_ports, right_ports = [""], [""]
        left_id, right_id = left.uid, right.uid
        if left_id in data.keys():
            left_ports = data[left_id]
        if right_id in data.keys():
            right_ports = data[right_id]

        if len(left_ports) != len(right_ports):
            raise ValueError("Number of ports does not match")
        for left_port, right_port in zip(left_ports, right_ports):
            connect(
                eng,
                model_name,
                created_components[left],
                left_port,
                created_components[right],
                right_port,
            )
