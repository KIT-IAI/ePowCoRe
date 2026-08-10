from epowcore.gdf.load import Load, LoadType


def test_load_uses_general_type_by_default() -> None:
    load = Load(
        1,
        "General Load",
        active_power=1.0,
        reactive_power=0.2,
    )

    assert load.load_type is LoadType.GENERAL


def test_load_can_be_created_as_low_voltage() -> None:
    load = Load(
        2,
        "Low Voltage Load",
        active_power=0.1,
        reactive_power=0.02,
        load_type=LoadType.LOW_VOLTAGE,
    )

    assert load.load_type is LoadType.LOW_VOLTAGE