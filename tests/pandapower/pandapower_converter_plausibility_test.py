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


def test_post_export_check_is_disabled_by_default() -> None:
    converter = PandapowerConverter()
    model = create_simple_model()

    returned_model = converter._post_export(model, "test")

    assert returned_model is model
    assert converter.plausibility_result is None


def test_post_export_check_runs_when_enabled(tmp_path) -> None:
    converter = PandapowerConverter(
        run_plausibility_check=True,
        plausibility_output_dir=str(tmp_path),
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