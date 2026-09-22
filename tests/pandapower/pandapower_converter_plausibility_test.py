import pandapower

from epowcore.pandapower.pandapower_converter import PandapowerConverter
from epowcore.pandapower.pandapower_model import PandapowerModel


def create_simple_model() -> PandapowerModel:
    net = pandapower.create_empty_network()

    bus = pandapower.create_bus(
        net,
        vn_kv=20.0,
        geodata=(0.0, 0.0),
    )

    pandapower.create_ext_grid(
        net,
        bus=bus,
        vm_pu=1.0,
    )

    return PandapowerModel(network=net)


def create_generator_model(vm_pu: float) -> PandapowerModel:
    net = pandapower.create_empty_network()

    slack_bus = pandapower.create_bus(
        net,
        vn_kv=20.0,
        geodata=(0.0, 0.0),
    )
    gen_bus = pandapower.create_bus(
        net,
        vn_kv=20.0,
        geodata=(1.0, 0.0),
    )

    pandapower.create_ext_grid(
        net,
        bus=slack_bus,
        vm_pu=1.0,
    )

    pandapower.create_line_from_parameters(
        net,
        from_bus=slack_bus,
        to_bus=gen_bus,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )

    pandapower.create_gen(
        net,
        bus=gen_bus,
        p_mw=1.0,
        vm_pu=vm_pu,
        name="Test Generator",
    )

    return PandapowerModel(network=net)


def test_post_export_check_is_disabled_by_default() -> None:
    converter = PandapowerConverter()
    model = create_simple_model()

    returned_model = converter._post_export(model, "test")

    assert returned_model is model
    assert converter.plausibility_result is None


def test_post_export_check_runs_when_enabled(tmp_path) -> None:
    converter = PandapowerConverter(
        run_plausibility_check=True,
        plausibility_output_path=str(tmp_path),
    )
    model = create_simple_model()

    returned_model = converter._post_export(model, "test")
    output_file = tmp_path / "test_plausibility.json"

    assert returned_model is model
    assert converter.plausibility_result is not None
    assert converter.plausibility_result.converged
    assert converter.plausibility_result.successful
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_generator_soft_voltage_violation() -> None:
    converter = PandapowerConverter(run_plausibility_check=True)
    model = create_generator_model(vm_pu=1.15)

    converter._post_export(model, "test")

    assert converter.plausibility_result is not None
    assert len(converter.plausibility_result.generator_soft_voltage_violations) == 1
    assert len(converter.plausibility_result.generator_hard_voltage_violations) == 0

    violation = converter.plausibility_result.generator_soft_voltage_violations[0]

    assert violation["component"] == "gen"
    assert violation["name"] == "Test Generator"
    assert violation["vm_pu"] == 1.15


def test_generator_hard_voltage_violation() -> None:
    converter = PandapowerConverter(run_plausibility_check=True)
    model = create_generator_model(vm_pu=1.25)

    converter._post_export(model, "test")

    assert converter.plausibility_result is not None
    assert len(converter.plausibility_result.generator_soft_voltage_violations) == 0
    assert len(converter.plausibility_result.generator_hard_voltage_violations) == 1

    violation = converter.plausibility_result.generator_hard_voltage_violations[0]

    assert violation["component"] == "gen"
    assert violation["name"] == "Test Generator"
    assert violation["vm_pu"] == 1.25

def create_isolated_area_model() -> PandapowerModel:
    net = pandapower.create_empty_network()

    supplied_bus = pandapower.create_bus(
        net,
        vn_kv=20.0,
        geodata=(0.0, 0.0),
        name="Supplied Bus",
    )

    isolated_bus = pandapower.create_bus(
        net,
        vn_kv=20.0,
        geodata=(5.0, 3.0),
        name="Isolated Bus",
    )

    pandapower.create_ext_grid(
        net,
        bus=supplied_bus,
        vm_pu=1.0,
    )

    return PandapowerModel(network=net)