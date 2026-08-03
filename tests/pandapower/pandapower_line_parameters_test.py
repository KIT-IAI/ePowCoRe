import math

import pytest

from epowcore.pandapower.pandapower_converter import PandapowerConverter
from tests.helpers.gdf_component_creator import GdfTestComponentCreator


def test_low_voltage_line_parameters_are_exported_correctly() -> None:
    creator = GdfTestComponentCreator(base_frequency=50.0)

    bus_a = creator.create_bus(name="LV Bus A")
    bus_b = creator.create_bus(name="LV Bus B")
    line = creator.create_tline(name="400 V Line")

    bus_a.nominal_voltage = 0.4
    bus_b.nominal_voltage = 0.4

    line.rating = 0.4
    line.length = 1.0
    line.r1 = 0.1
    line.x1 = 0.2
    line.b1 = 50.0
    line.parallel_lines = 2

    creator.core_model.add_connection(line, bus_a, "A")
    creator.core_model.add_connection(line, bus_b, "B")

    network = PandapowerConverter().from_gdf(
        core_model=creator.core_model,
        name="low_voltage_line_test",
        log_path=None,
    ).network

    exported_line = network.line.loc[
        network.line["name"] == "400 V Line"
    ].iloc[0]

    expected_current_ka = line.rating / (
        math.sqrt(3) * bus_a.nominal_voltage
    )

    expected_capacitance_nf_per_km = (
        line.b1 * 1e3
    ) / (2 * math.pi * creator.core_model.base_frequency)

    assert exported_line["max_i_ka"] == pytest.approx(expected_current_ka)
    assert exported_line["length_km"] == pytest.approx(line.length)
    assert exported_line["r_ohm_per_km"] == pytest.approx(line.r1)
    assert exported_line["x_ohm_per_km"] == pytest.approx(line.x1)
    assert exported_line["c_nf_per_km"] == pytest.approx(
        expected_capacitance_nf_per_km
    )
    assert exported_line["parallel"] == line.parallel_lines

def test_line_export_rejects_zero_nominal_voltage() -> None:
    creator = GdfTestComponentCreator(base_frequency=50.0)

    bus_a = creator.create_bus(name="Invalid Bus A")
    bus_b = creator.create_bus(name="Invalid Bus B")
    line = creator.create_tline(name="Invalid Line")

    bus_a.nominal_voltage = 0.0
    bus_b.nominal_voltage = 0.0

    creator.core_model.add_connection(line, bus_a, "A")
    creator.core_model.add_connection(line, bus_b, "B")

    with pytest.raises(ValueError, match="nominal voltage"):
        PandapowerConverter().from_gdf(
            core_model=creator.core_model,
            name="invalid_voltage_test",
            log_path=None,
        )