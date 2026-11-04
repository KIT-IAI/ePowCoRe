
"""Round-trip validation of the pandapower multi-voltage reference network.

GitHub issue: https://github.com/KIT-IAI/ePowCoRe/issues/40
"""

import pandapower as pp
import pytest
from pandapower.networks import example_multivoltage

from epowcore.pandapower.pandapower_converter import PandapowerConverter
from epowcore.pandapower.pandapower_model import PandapowerModel


COMPONENT_TYPES = (
    "bus",
    "line",
    "trafo",
    "trafo3w",
    "load",
    "sgen",
    "gen",
    "ext_grid",
    "switch",
    "shunt",
    "xward",
    "impedance",
)


@pytest.fixture(scope="module")
def reference_network():
    """Load the unmodified pandapower reference network."""
    return example_multivoltage()


@pytest.fixture(scope="module")
def roundtrip_network(reference_network):
    """Convert pandapower -> GDF -> pandapower."""
    converter = PandapowerConverter()

    gdf = converter.to_gdf(
        PandapowerModel(network=reference_network)
    )

    return converter.from_gdf(
        core_model=gdf,
        name="PandapowerReference40",
    ).network


def test_reference_network_power_flow(reference_network):
    """Ensure the original network is a valid baseline."""
    pp.runpp(reference_network, numba=False)
    assert reference_network.converged


def test_roundtrip_power_flow(roundtrip_network):
    """Ensure the reconstructed network can solve a power flow."""
    pp.runpp(roundtrip_network, numba=False)
    assert roundtrip_network.converged


def test_roundtrip_component_counts(
    reference_network, roundtrip_network
):
    """Detect missing or additional network components."""
    differences = {}

    for component in COMPONENT_TYPES:
        original_count = len(reference_network[component])
        converted_count = len(roundtrip_network[component])

        if original_count != converted_count:
            differences[component] = {
                "original": original_count,
                "converted": converted_count,
            }

    assert not differences, (
        "Round-trip component count mismatches: "
        f"{differences}"
    )


def test_roundtrip_voltage_levels(
    reference_network, roundtrip_network
):
    """Verify that nominal bus voltage levels are preserved."""
    original = sorted(reference_network.bus.vn_kv.tolist())
    converted = sorted(roundtrip_network.bus.vn_kv.tolist())

    assert converted == pytest.approx(original)


def test_roundtrip_bus_voltage_results(
    reference_network, roundtrip_network
):
    """Compare bus voltage magnitudes after power flow."""

    pp.runpp(reference_network, numba=False)
    pp.runpp(roundtrip_network, numba=False)

    original = reference_network.res_bus.join(
        reference_network.bus[["name"]],
        how="left",
    )

    reconstructed = roundtrip_network.res_bus.join(
        roundtrip_network.bus[["name"]],
        how="left",
    )

    original = original.set_index("name")
    reconstructed = reconstructed.set_index("name")

    assert original.index.is_unique
    assert reconstructed.index.is_unique
    assert set(original.index) == set(reconstructed.index)

    differences = (
        original["vm_pu"] - reconstructed["vm_pu"]
    ).abs()

    print(
        "\nMaximum bus voltage difference:",
        differences.max(),
        "pu",
    )

    assert differences.max() < 1e-4


def test_roundtrip_two_winding_transformer_parameters(
    reference_network, roundtrip_network
):
    """Verify two-winding transformer electrical parameters."""

    columns = [
        "sn_mva",
        "vn_hv_kv",
        "vn_lv_kv",
        "vk_percent",
        "vkr_percent",
        "pfe_kw",
        "i0_percent",
        "shift_degree",
    ]

    original = reference_network.trafo.set_index("name")
    reconstructed = roundtrip_network.trafo.set_index("name")

    assert set(original.index) == set(reconstructed.index)

    for name in original.index:
        for column in columns:
            assert reconstructed.loc[name, column] == pytest.approx(
                original.loc[name, column],
                rel=1e-6,
                abs=1e-8,
            ), f"{name}: {column} differs"


@pytest.mark.parametrize(
    "component_type, bus_columns",
    [
        ("line", ("from_bus", "to_bus")),
        ("trafo", ("hv_bus", "lv_bus")),
        ("trafo3w", ("hv_bus", "mv_bus", "lv_bus")),
        ("impedance", ("from_bus", "to_bus")),
        ("load", ("bus",)),
        ("sgen", ("bus",)),
        ("gen", ("bus",)),
        ("ext_grid", ("bus",)),
        ("shunt", ("bus",)),
        ("xward", ("bus",)),
    ],
)
def test_roundtrip_component_connections(
    reference_network,
    roundtrip_network,
    component_type,
    bus_columns,
):
    """Verify component connections using bus names."""

    original = getattr(reference_network, component_type)
    reconstructed = getattr(roundtrip_network, component_type)

    assert len(original) == len(reconstructed)

    for source, target in zip(
        original.itertuples(index=False),
        reconstructed.itertuples(index=False),
    ):
        for column in bus_columns:
            source_bus_index = getattr(source, column)
            target_bus_index = getattr(target, column)

            source_bus_name = reference_network.bus.loc[
                source_bus_index, "name"
            ]
            target_bus_name = roundtrip_network.bus.loc[
                target_bus_index, "name"
            ]

            assert source_bus_name == target_bus_name, (
                f"{component_type}: {column} mismatch: "
                f"{source_bus_name} != {target_bus_name}"
            )


def test_roundtrip_switches(reference_network, roundtrip_network):
    """Compare switch types, connections, and states."""

    def switch_signature(net, switch):
        bus_name = net.bus.loc[int(switch["bus"]), "name"]
        element_type = switch["et"]
        element_index = int(switch["element"])

        if element_type == "b":
            element_name = net.bus.loc[element_index, "name"]
        elif element_type == "l":
            element_name = net.line.loc[element_index, "name"]
        elif element_type == "t":
            element_name = net.trafo.loc[element_index, "name"]
        elif element_type == "t3":
            element_name = net.trafo3w.loc[element_index, "name"]
        else:
            raise AssertionError(
                f"Unexpected switch element type: {element_type}"
            )

        return (
            bus_name,
            element_type,
            element_name,
            bool(switch["closed"]),
        )

    original_signatures = sorted(
        switch_signature(reference_network, row)
        for _, row in reference_network.switch.iterrows()
    )

    reconstructed_signatures = sorted(
        switch_signature(roundtrip_network, row)
        for _, row in roundtrip_network.switch.iterrows()
    )

    assert original_signatures == reconstructed_signatures


@pytest.mark.parametrize(
    "component_type, columns",
    [
        (
            "impedance",
            (
                "rft_pu", "xft_pu", "rtf_pu",
                "xtf_pu", "sn_mva",
            ),
        ),
        (
            "xward",
            (
                "ps_mw", "qs_mvar", "pz_mw", "qz_mvar",
                "r_ohm", "x_ohm", "vm_pu",
            ),
        ),
        (
            "shunt",
            ("p_mw", "q_mvar", "vn_kv"),
        ),
        (
            "load",
            ("p_mw", "q_mvar"),
        ),
        (
            "line",
            (
                "length_km", "r_ohm_per_km",
                "x_ohm_per_km", "c_nf_per_km",
            ),
        ),
        (
            "trafo3w",
            (
                "sn_hv_mva", "sn_mv_mva", "sn_lv_mva",
                "vn_hv_kv", "vn_mv_kv", "vn_lv_kv",
                "vk_hv_percent", "vk_mv_percent", "vk_lv_percent",
                "vkr_hv_percent", "vkr_mv_percent", "vkr_lv_percent",
                "shift_mv_degree", "shift_lv_degree",
                "tap_step_percent",
            ),
        ),
    ],
)
def test_roundtrip_component_parameters(
    reference_network,
    roundtrip_network,
    component_type,
    columns,
):
    """Compare electrical parameters by component name."""

    original = getattr(reference_network, component_type)
    converted = getattr(roundtrip_network, component_type)

    original = original.set_index("name")
    converted = converted.set_index("name")

    assert original.index.is_unique
    assert converted.index.is_unique
    assert set(original.index) == set(converted.index)

    for name in original.index:
        for column in columns:
            assert converted.loc[name, column] == pytest.approx(
                original.loc[name, column],
                rel=1e-6,
                abs=1e-8,
            ), f"{component_type} '{name}': parameter '{column}' differs"



@pytest.mark.parametrize(
    "element_type, result_columns",
    [
        ("bus", ("vm_pu", "va_degree")),
        ("line", ("p_from_mw", "q_from_mvar", "p_to_mw", "q_to_mvar")),
        ("trafo", ("p_hv_mw", "q_hv_mvar", "p_lv_mw", "q_lv_mvar")),
        (
            "trafo3w",
            (
                "p_hv_mw", "q_hv_mvar",
                "p_mv_mw", "q_mv_mvar",
                "p_lv_mw", "q_lv_mvar",
            ),
        ),
        ("impedance", ("p_from_mw", "q_from_mvar", "p_to_mw", "q_to_mvar")),
    ],
)
def test_roundtrip_loadflow_results(
    reference_network,
    roundtrip_network,
    element_type,
    result_columns,
):
    """Compare original and reconstructed power-flow results."""

    pp.runpp(reference_network, numba=False)
    pp.runpp(roundtrip_network, numba=False)

    source_elements = getattr(reference_network, element_type)
    target_elements = getattr(roundtrip_network, element_type)

    source_results = getattr(reference_network, f"res_{element_type}")
    target_results = getattr(roundtrip_network, f"res_{element_type}")

    source = source_results.join(source_elements[["name"]]).set_index("name")
    target = target_results.join(target_elements[["name"]]).set_index("name")

    assert source.index.is_unique
    assert target.index.is_unique
    assert set(source.index) == set(target.index)

    for name in source.index:
        for column in result_columns:
            assert target.loc[name, column] == pytest.approx(
                source.loc[name, column],
                rel=1e-5,
                abs=1e-5,
            ), (
                f"{element_type} '{name}': "
                f"{column} differs"
            )

