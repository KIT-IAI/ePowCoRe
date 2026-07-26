import json
import os
import pathlib
import sys
import unittest
from zipfile import Path

from helpers.gdf_component_creator import GdfTestComponentCreator

from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.utils import get_connected_bus
from epowcore.generic.manipulation.flatten import flatten

PATH = pathlib.Path(__file__).parent.resolve()


class UtilsTest(unittest.TestCase):
    """Test the utility functions of the gdf package."""

    # @unittest.skip("tmp")
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
        PATH = pathlib.Path(__file__).parent.parent.resolve()

        with open(
            PATH.parent.parent / "tests/models/gdf/IEEE39_gdf.json", "r", encoding="utf-8"
        ) as file:
            data_str = file.read()
            data = json.loads(data_str)
            core_model = CoreModel.import_dict(data)
            # flatten(core_model)  # if the mode lis flattened this also fails

        assert core_model.sanity_check()

    def test_sanity_check_IEEE39_flat(self) -> None:
        PATH = pathlib.Path(__file__).parent.parent.resolve()

        with open(
            PATH.parent.parent / "tests/models/gdf/IEEE39-flat_gdf.json", "r", encoding="utf-8"
        ) as file:
            data_str = file.read()
            data = json.loads(data_str)
            core_model = CoreModel.import_dict(data)

        assert core_model.sanity_check()

    # def test_sanity_check_IEEE9(self) -> None:
    #    PATH = pathlib.Path(__file__).parent.parent.resolve()

    #    with open(
    #        PATH.parent.parent / "tests/models/gdf/IEEE9_gdf.json", "r", encoding="utf-8"
    #    ) as file:
    #        data_str = file.read()
    #        data = json.loads(data_str)
    #        core_model = CoreModel.import_dict(data)

    #    assert core_model.sanity_check()


if __name__ == "__main__":
    unittest.main()
