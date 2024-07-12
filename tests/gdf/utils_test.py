import pathlib
import unittest
from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.data_structure import DataStructure

from epowcore.gdf.utils import get_connected_bus
from tests.helpers.gdf_component_creator import GdfTestComponentCreator

PATH = pathlib.Path(__file__).parent.resolve()


class UtilsTest(unittest.TestCase):
    """Test the utility functions of the gdf package."""

    # @unittest.skip("tmp")
    def test_get_connected_bus(self) -> None:
        ds = DataStructure(base_frequency=50.0)

        bus_a = Bus(1, "Bus A", lf_bus_type=LFBusType.PQ)
        bus_b = Bus(2, "Bus B", lf_bus_type=LFBusType.PQ)

        ds.add_component(bus_a)
        ds.add_component(bus_b)

        test_component_creator = GdfTestComponentCreator(50.0)
        tline = test_component_creator.create_tline("TLine")
        ds.add_component(tline)

        ds.add_connection(tline, bus_a, "A")
        ds.add_connection(tline, bus_b, "B")

        bus = get_connected_bus(ds.graph, tline)
        self.assertIn(bus, (bus_a, bus_b))


if __name__ == "__main__":
    unittest.main()