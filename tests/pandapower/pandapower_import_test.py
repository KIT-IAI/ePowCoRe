import pandapower
import math
import pytest
from epowcore.gdf.bus import Bus, BusType, LFBusType
from epowcore.gdf.load import Load
from epowcore.pandapower.pandapower_converter import PandapowerConverter
from epowcore.pandapower.pandapower_model import PandapowerModel
from epowcore.gdf.external_grid import ExternalGrid, ExternalGridType
from epowcore.gdf.generators.static_generator import StaticGenerator
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.switch import Switch
import pandapower.networks as pn

def test_import_bus_from_pandapower() -> None:
    net = pandapower.create_empty_network(
        f_hz=50.0,
        sn_mva=100.0,
    )

    pandapower.create_bus(
        net,
        name="Test Bus",
        vn_kv=20.0,
        type="b",
    )

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    buses = core_model.type_list(Bus)

    assert len(buses) == 1

    bus = buses[0]

    assert bus.name == "Test Bus"
    assert bus.nominal_voltage == 20.0
    assert bus.bus_type == BusType.BUSBAR
    assert bus.lf_bus_type == LFBusType.PQ


def test_import_load_from_pandapower() -> None:
    net = pandapower.create_empty_network(
        f_hz=50.0,
        sn_mva=100.0,
    )

    bus_index = pandapower.create_bus(
        net,
        name="Load Bus",
        vn_kv=20.0,
    )

    pandapower.create_load(
        net,
        bus=bus_index,
        name="Test Load",
        p_mw=5.0,
        q_mvar=2.0,
    )

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    loads = core_model.type_list(Load)
    buses = core_model.type_list(Bus)

    assert len(loads) == 1
    assert len(buses) == 1

    load = loads[0]
    bus = buses[0]

    assert load.name == "Test Load"
    assert load.active_power == 5.0
    assert load.reactive_power == 2.0

    assert core_model.graph.has_edge(load, bus)

def test_import_external_grid_from_pandapower() -> None:
    net = pandapower.create_empty_network(
        f_hz=50.0,
        sn_mva=100.0,
    )

    bus_index = pandapower.create_bus(
        net,
        name="Slack Bus",
        vn_kv=110.0,
    )

    pandapower.create_ext_grid(
        net,
        bus=bus_index,
        name="Grid Connection",
        vm_pu=1.02,
    )

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    external_grids = core_model.type_list(ExternalGrid)
    buses = core_model.type_list(Bus)

    assert len(external_grids) == 1
    assert len(buses) == 1

    external_grid = external_grids[0]
    bus = buses[0]

    assert external_grid.name == "Grid Connection"
    assert external_grid.u_setp == 1.02
    assert external_grid.bus_type == ExternalGridType.SL

    assert bus.lf_bus_type == LFBusType.SL
    assert core_model.graph.has_edge(external_grid, bus)

def test_import_static_generator_from_pandapower() -> None:
    net = pandapower.create_empty_network(
        f_hz=50.0,
        sn_mva=100.0,
    )

    bus_index = pandapower.create_bus(
        net,
        name="Generator Bus",
        vn_kv=20.0,
    )

    pandapower.create_sgen(
        net,
        bus=bus_index,
        name="Test Static Generator",
        p_mw=4.0,
        q_mvar=1.5,
        sn_mva=5.0,
    )

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    generators = core_model.type_list(StaticGenerator)
    buses = core_model.type_list(Bus)

    assert len(generators) == 1
    assert len(buses) == 1

    generator = generators[0]
    bus = buses[0]

    assert generator.name == "Test Static Generator"
    assert generator.active_power == 4.0
    assert generator.reactive_power == 1.5
    assert generator.rated_apparent_power == 5.0

    assert core_model.graph.has_edge(generator, bus)

def test_import_synchronous_machine_from_pandapower() -> None:
    net = pandapower.create_empty_network(
        f_hz=50.0,
        sn_mva=100.0,
    )

    bus_index = pandapower.create_bus(
        net,
        name="Generator Bus",
        vn_kv=110.0,
    )

    pandapower.create_gen(
        net,
        bus=bus_index,
        name="Test Generator",
        p_mw=50.0,
        vm_pu=1.01,
        sn_mva=60.0,
        min_p_mw=10.0,
        max_p_mw=55.0,
        min_q_mvar=-20.0,
        max_q_mvar=25.0,
    )

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    generators = core_model.type_list(SynchronousMachine)
    buses = core_model.type_list(Bus)

    assert len(generators) == 1
    assert len(buses) == 1

    generator = generators[0]
    bus = buses[0]

    assert generator.name == "Test Generator"
    assert generator.active_power == 50.0
    assert generator.rated_apparent_power == 60.0
    assert generator.rated_voltage == 110.0
    assert generator.voltage_set_point == 1.01
    assert generator.p_min == 10.0
    assert generator.p_max == 55.0
    assert generator.q_min == -20.0
    assert generator.q_max == 25.0

    assert generator.inertia_constant == 4.475
    assert generator.synchronous_reactance_x == 1.996

    assert core_model.graph.has_edge(generator, bus)

def test_import_line_from_pandapower() -> None:
    net = pandapower.create_empty_network(
        f_hz=50.0,
        sn_mva=100.0,
    )

    bus_a = pandapower.create_bus(
        net,
        name="Bus A",
        vn_kv=110.0,
    )

    bus_b = pandapower.create_bus(
        net,
        name="Bus B",
        vn_kv=110.0,
    )

    pandapower.create_line_from_parameters(
        net,
        from_bus=bus_a,
        to_bus=bus_b,
        length_km=10.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.2,
        c_nf_per_km=10.0,
        max_i_ka=0.5,
        name="Test Line",
    )

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    lines = core_model.type_list(TLine)
    buses = core_model.type_list(Bus)

    assert len(lines) == 1
    assert len(buses) == 2

    line = lines[0]

    assert line.name == "Test Line"
    assert line.length == 10.0
    assert line.r1 == 0.1
    assert line.x1 == 0.2
    assert line.parallel_lines == 1

    assert line.b1 == pytest.approx(
        2 * math.pi * 50.0 * 10.0 / 1000
    )

    assert line.rating == pytest.approx(
        math.sqrt(3) * 110.0 * 0.5
    )

    assert core_model.graph.has_edge(line, buses[0])
    assert core_model.graph.has_edge(line, buses[1])

def test_import_two_winding_transformer_from_pandapower() -> None:
    net = pandapower.create_empty_network(
        f_hz=50.0,
        sn_mva=100.0,
    )

    hv_bus = pandapower.create_bus(
        net,
        name="HV Bus",
        vn_kv=110.0,
    )

    lv_bus = pandapower.create_bus(
        net,
        name="LV Bus",
        vn_kv=20.0,
    )

    pandapower.create_transformer_from_parameters(
        net,
        hv_bus=hv_bus,
        lv_bus=lv_bus,
        name="Test Transformer",
        sn_mva=40.0,
        vn_hv_kv=110.0,
        vn_lv_kv=20.0,
        vk_percent=10.0,
        vkr_percent=0.5,
        pfe_kw=25.0,
        i0_percent=0.1,
        shift_degree=30.0,
    )

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    transformers = core_model.type_list(TwoWindingTransformer)
    buses = core_model.type_list(Bus)

    assert len(transformers) == 1
    assert len(buses) == 2

    transformer = transformers[0]

    assert transformer.name == "Test Transformer"
    assert transformer.rating == 40.0
    assert transformer.voltage_hv == 110.0
    assert transformer.voltage_lv == 20.0
    assert transformer.r1pu == pytest.approx(0.005)
    assert transformer.x1pu == pytest.approx(
        math.sqrt(0.1**2 - 0.005**2)
    )
    assert transformer.pfe_kw == 25.0
    assert transformer.no_load_current == 0.1
    assert transformer.phase_shift_30 == 1

    assert core_model.graph.has_edge(transformer, buses[0])
    assert core_model.graph.has_edge(transformer, buses[1])

def test_import_bus_switch_from_pandapower() -> None:
    net = pandapower.create_empty_network(
        f_hz=50.0,
        sn_mva=100.0,
    )

    bus_a = pandapower.create_bus(
        net,
        name="Bus A",
        vn_kv=20.0,
    )

    bus_b = pandapower.create_bus(
        net,
        name="Bus B",
        vn_kv=20.0,
    )

    pandapower.create_switch(
        net,
        bus=bus_a,
        element=bus_b,
        et="b",
        closed=True,
        name="Test Switch",
    )

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    switches = core_model.type_list(Switch)
    buses = core_model.type_list(Bus)

    assert len(switches) == 1
    assert len(buses) == 2

    switch = switches[0]

    assert switch.name == "Test Switch"
    assert switch.closed is True

    assert core_model.graph.has_edge(switch, buses[0])
    assert core_model.graph.has_edge(switch, buses[1])

def test_import_line_switch_from_pandapower() -> None:
    net = pandapower.create_empty_network(
        f_hz=50.0,
        sn_mva=100.0,
    )

    bus_a = pandapower.create_bus(
        net,
        name="Bus A",
        vn_kv=20.0,
    )

    bus_b = pandapower.create_bus(
        net,
        name="Bus B",
        vn_kv=20.0,
    )

    line_index = pandapower.create_line_from_parameters(
        net,
        from_bus=bus_a,
        to_bus=bus_b,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.2,
        c_nf_per_km=10.0,
        max_i_ka=0.4,
        name="Test Line",
    )

    pandapower.create_switch(
        net,
        bus=bus_a,
        element=line_index,
        et="l",
        closed=False,
        name="Line Switch",
    )

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    switches = core_model.type_list(Switch)
    lines = core_model.type_list(TLine)

    assert len(switches) == 1
    assert len(lines) == 1

    switch = switches[0]
    line = lines[0]

    assert switch.name == "Line Switch"
    assert switch.closed is False

    assert core_model.graph.has_edge(switch, line)

def test_import_pandapower_example_network() -> None:
    net = pn.simple_four_bus_system()

    core_model = PandapowerConverter().to_gdf(
        PandapowerModel(network=net)
    )

    assert len(core_model.type_list(Bus)) == len(net.bus)
    assert len(core_model.type_list(Load)) == len(net.load)
    assert len(core_model.type_list(ExternalGrid)) == len(net.ext_grid)
    assert len(core_model.type_list(TLine)) == len(net.line)

    assert len(core_model.graph.nodes) > 0
    assert len(core_model.graph.edges) > 0