import pandapower

from epowcore.plausibility.pandapower_checker import (
    PandapowerPlausibilityChecker,
)


def test_converging_network() -> None:
    net = pandapower.create_empty_network()

    bus_1 = pandapower.create_bus(net, vn_kv=20.0)
    bus_2 = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=bus_1, vm_pu=1.0)
    pandapower.create_line_from_parameters(
        net,
        from_bus=bus_1,
        to_bus=bus_2,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )
    pandapower.create_load(net, bus=bus_2, p_mw=0.1, q_mvar=0.05)

    result = PandapowerPlausibilityChecker().check(net)

    print("Converged:", result.converged)
    print("Errors:", result.errors)

    assert result.converged
    assert not result.errors


def test_detects_voltage_violation() -> None:
    net = pandapower.create_empty_network()

    bus_1 = pandapower.create_bus(net, vn_kv=20.0)
    bus_2 = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=bus_1, vm_pu=1.0)
    pandapower.create_line_from_parameters(
        net,
        from_bus=bus_1,
        to_bus=bus_2,
        length_km=20.0,
        r_ohm_per_km=1.0,
        x_ohm_per_km=0.5,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )
    pandapower.create_load(net, bus=bus_2, p_mw=2.0, q_mvar=1.0)

    result = PandapowerPlausibilityChecker().check(net)

    print("Soft voltage violations:", result.soft_voltage_violations)

    assert result.converged
    assert result.soft_voltage_violations
    assert not result.hard_voltage_violations


def test_detects_overloaded_line() -> None:
    net = pandapower.create_empty_network()

    bus_1 = pandapower.create_bus(net, vn_kv=20.0)
    bus_2 = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=bus_1, vm_pu=1.0)
    pandapower.create_line_from_parameters(
        net,
        from_bus=bus_1,
        to_bus=bus_2,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=0.01,
    )
    pandapower.create_load(net, bus=bus_2, p_mw=1.0, q_mvar=0.2)

    result = PandapowerPlausibilityChecker().check(net)

    print("Overloaded lines:", result.overloaded_lines)

    assert result.converged
    assert result.overloaded_lines


def test_detects_overloaded_transformer() -> None:
    net = pandapower.create_empty_network()

    bus_hv = pandapower.create_bus(net, vn_kv=110.0)
    bus_lv = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=bus_hv, vm_pu=1.0)
    pandapower.create_transformer_from_parameters(
        net,
        hv_bus=bus_hv,
        lv_bus=bus_lv,
        sn_mva=0.1,
        vn_hv_kv=110.0,
        vn_lv_kv=20.0,
        vk_percent=10.0,
        vkr_percent=0.5,
        pfe_kw=0.0,
        i0_percent=0.0,
    )
    pandapower.create_load(
        net,
        bus=bus_lv,
        p_mw=0.2,
        q_mvar=0.05,
    )

    result = PandapowerPlausibilityChecker().check(net)

    print("Overloaded transformers:", result.overloaded_transformers)

    assert result.converged
    assert result.overloaded_transformers

def test_detects_hard_voltage_violation() -> None:
    net = pandapower.create_empty_network()

    bus_1 = pandapower.create_bus(net, vn_kv=20.0)
    bus_2 = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=bus_1, vm_pu=1.0)
    pandapower.create_line_from_parameters(
        net,
        from_bus=bus_1,
        to_bus=bus_2,
        length_km=30.0,
        r_ohm_per_km=1.0,
        x_ohm_per_km=0.5,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )
    pandapower.create_load(
        net,
        bus=bus_2,
        p_mw=2.5,
        q_mvar=1.5,
    )

    result = PandapowerPlausibilityChecker().check(net)

    print("Hard voltage violations:", result.hard_voltage_violations)

    assert result.converged
    assert result.hard_voltage_violations

def test_detects_isolated_area() -> None:
    net = pandapower.create_empty_network()

    supplied_bus = pandapower.create_bus(net, vn_kv=20.0)
    isolated_bus_1 = pandapower.create_bus(net, vn_kv=20.0)
    isolated_bus_2 = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=supplied_bus, vm_pu=1.0)

    pandapower.create_line_from_parameters(
        net,
        from_bus=isolated_bus_1,
        to_bus=isolated_bus_2,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )

    result = PandapowerPlausibilityChecker().check(net)

    assert result.isolated_areas
    assert result.isolated_areas[0] == [isolated_bus_1, isolated_bus_2]

def test_successful_summary() -> None:
    net = pandapower.create_empty_network()

    bus_1 = pandapower.create_bus(net, vn_kv=20.0)
    bus_2 = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=bus_1, vm_pu=1.0)
    pandapower.create_line_from_parameters(
        net,
        from_bus=bus_1,
        to_bus=bus_2,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )
    pandapower.create_load(net, bus=bus_2, p_mw=0.1, q_mvar=0.05)

    result = PandapowerPlausibilityChecker().check(net)

    assert result.successful
    assert result.summary() == (
        "Plausibility check successful. No issues detected."
    )

def test_summary_reports_issue_counts() -> None:
    net = pandapower.create_empty_network()

    bus_1 = pandapower.create_bus(net, vn_kv=20.0)
    bus_2 = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=bus_1, vm_pu=1.0)
    pandapower.create_line_from_parameters(
        net,
        from_bus=bus_1,
        to_bus=bus_2,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=0.01,
    )
    pandapower.create_load(net, bus=bus_2, p_mw=1.0, q_mvar=0.2)

    result = PandapowerPlausibilityChecker().check(net)
    summary = result.summary()

    assert "Overloaded lines: 1" in summary
    assert not result.successful

def test_detects_multiple_isolated_areas() -> None:
    net = pandapower.create_empty_network()

    supplied_bus = pandapower.create_bus(net, vn_kv=20.0)
    island_1_bus_1 = pandapower.create_bus(net, vn_kv=20.0)
    island_1_bus_2 = pandapower.create_bus(net, vn_kv=20.0)
    island_2_bus = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=supplied_bus, vm_pu=1.0)

    pandapower.create_line_from_parameters(
        net,
        from_bus=island_1_bus_1,
        to_bus=island_1_bus_2,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )

    result = PandapowerPlausibilityChecker().check(net)

    assert len(result.isolated_areas) == 2
    assert sorted(result.isolated_areas) == sorted(
        [
            [island_1_bus_1, island_1_bus_2],
            [island_2_bus],
        ]
    )

def test_detects_multiple_isolated_areas() -> None:
    net = pandapower.create_empty_network()

    supplied_bus = pandapower.create_bus(net, vn_kv=20.0)
    island_1_bus_1 = pandapower.create_bus(net, vn_kv=20.0)
    island_1_bus_2 = pandapower.create_bus(net, vn_kv=20.0)
    island_2_bus = pandapower.create_bus(net, vn_kv=20.0)

    pandapower.create_ext_grid(net, bus=supplied_bus, vm_pu=1.0)

    pandapower.create_line_from_parameters(
        net,
        from_bus=island_1_bus_1,
        to_bus=island_1_bus_2,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )

    result = PandapowerPlausibilityChecker().check(net)

    assert len(result.isolated_areas) == 2
    assert sorted(result.isolated_areas) == sorted(
        [
            [island_1_bus_1, island_1_bus_2],
            [island_2_bus],
        ]
    )

def test_bus_geodata_is_exported() -> None:
    net = pandapower.create_empty_network()

    bus_index = pandapower.create_bus(
        net,
        vn_kv=20.0,
        geodata=(1.0, 2.0),
    )

    assert net.bus.at[bus_index, "geo"] is not None

def test_plots_isolated_areas(tmp_path) -> None:
    net = pandapower.create_empty_network()

    supplied_bus = pandapower.create_bus(
        net,
        vn_kv=20.0,
        geodata=(0.0, 0.0),
    )
    isolated_bus_1 = pandapower.create_bus(
        net,
        vn_kv=20.0,
        geodata=(1.0, 1.0),
    )
    isolated_bus_2 = pandapower.create_bus(
        net,
        vn_kv=20.0,
        geodata=(2.0, 1.0),
    )

    pandapower.create_ext_grid(
        net,
        bus=supplied_bus,
        vm_pu=1.0,
    )

    pandapower.create_line_from_parameters(
        net,
        from_bus=isolated_bus_1,
        to_bus=isolated_bus_2,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )

    checker = PandapowerPlausibilityChecker()
    result = checker.check(net)

    output_file = tmp_path / "isolated_areas.png"

    checker.plot_isolated_areas(
        net,
        result,
        str(output_file),
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0
