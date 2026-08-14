import json
import pathlib
import unittest

from helpers.gdf_component_creator import GdfTestComponentCreator

from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.subsystem import Subsystem
from epowcore.gdf.utils import get_connected_bus

PATH = pathlib.Path(__file__).parent.resolve()


class UtilsTest(unittest.TestCase):
    """Test the utility functions of the gdf package."""

    def test_get_connected_bus(self) -> None:
        core_model = CoreModel(base_frequency=50.0)

        bus_a = Bus(1, "Bus A", lf_bus_type=LFBusType.PQ)
        bus_b = Bus(2, "Bus B", lf_bus_type=LFBusType.PQ)

        core_model.add_component(bus_a)
        core_model.add_component(bus_b)

        test_component_creator = GdfTestComponentCreator(50.0)
        tline = test_component_creator.create_tline("TLine")
        core_model.add_component(tline)

        core_model.add_connection(tline, bus_a, "A")
        core_model.add_connection(tline, bus_b, "B")

        bus = get_connected_bus(core_model.graph, tline)
        self.assertIn(bus, (bus_a, bus_b))

    def test_sanity_check_IEEE39(self) -> None:
        path = pathlib.Path(__file__).parent.parent.resolve()

        with open(
            path.parent.parent / "tests/models/gdf/IEEE39_gdf.json",
            "r",
            encoding="utf-8",
        ) as file:
            data_str = file.read()
            data = json.loads(data_str)
            core_model = CoreModel.import_dict(data)

        self.assertFalse(core_model.sanity_check())

    def test_sanity_check_IEEE39_flat(self) -> None:
        path = pathlib.Path(__file__).parent.parent.resolve()

        with open(
            path.parent.parent / "tests/models/gdf/IEEE39-flat_gdf.json",
            "r",
            encoding="utf-8",
        ) as file:
            data_str = file.read()
            data = json.loads(data_str)
            core_model = CoreModel.import_dict(data)

        self.assertFalse(core_model.sanity_check())

    def test_sanity_check_valid_subsystem(self) -> None:
        """Sanity check succeeds when a subsystem graph is valid."""

        creator = GdfTestComponentCreator(50.0)
        core_model = creator.core_model

        tline = creator.create_tline("Line")
        bus_a = creator.create_bus("Bus A")
        bus_b = creator.create_bus("Bus B")

        core_model.add_connection(tline, bus_a, "A", "")
        core_model.add_connection(tline, bus_b, "B", "")

        Subsystem.from_components(core_model, [tline])

        self.assertTrue(core_model.sanity_check())

    def test_sanity_check_invalid_subsystem(self) -> None:
        """Sanity check fails when a required connector is missing inside a subsystem."""

        creator = GdfTestComponentCreator(50.0)
        core_model = creator.core_model

        tline = creator.create_tline("Line")
        bus_a = creator.create_bus("Bus A")
        bus_b = creator.create_bus("Bus B")

        core_model.add_connection(tline, bus_a, "A", "")
        core_model.add_connection(tline, bus_b, "B", "")

        subsystem = Subsystem.from_components(core_model, [tline])

        port = next(iter(subsystem.graph.neighbors(tline)))
        subsystem.graph.edges[tline, port][tline.uid] = []

        self.assertFalse(core_model.sanity_check())

    def test_sanity_check_IEEE399_valid(self) -> None:
        path = pathlib.Path(__file__).parent.parent.resolve()

        with open(
            path.parent.parent / "tests/models/gdf/IEEE399_gdf.json",
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
            core_model = CoreModel.import_dict(data)

        self.assertTrue(core_model.sanity_check())

if __name__ == "__main__":
    unittest.main()