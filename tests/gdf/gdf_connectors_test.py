import json
import pathlib
import unittest

from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.generic.manipulation.map_connectors import map_connectors
from tests.helpers.gdf_component_creator import GdfTestComponentCreator

PATH = pathlib.Path(__file__).parent.resolve()


class GdfConnectorsTest(unittest.TestCase):
    """Test the connectors in the CoreModel graph."""

    def test_add_connectors(self) -> None:
        """Add a component to the graph."""

        core_model = CoreModel(base_frequency=50.0)
        bus_a = Bus(1, "Bus A", lf_bus_type=LFBusType.PQ)
        bus_b = Bus(2, "Bus B", lf_bus_type=LFBusType.PQ)
        core_model.add_component(bus_a)
        core_model.add_component(bus_b)

        core_model.add_connection(bus_a, bus_b, "test1", "test2")
        self.assertEqual(core_model.get_connector_names(core_model.type_list(Bus)[0]), ["test1"])
        self.assertEqual(
            core_model.get_attached_to(core_model.type_list(Bus)[0], "test1"),
            [(core_model.type_list(Bus)[1], ["test2"])],
        )

    def test_map_connectors(self) -> None:
        """Add a component to the graph."""

        core_model = CoreModel(base_frequency=50.0)
        bus_a = Bus(1, "Bus A", lf_bus_type=LFBusType.PQ)
        bus_b = Bus(2, "Bus B", lf_bus_type=LFBusType.PQ)
        core_model.add_component(bus_a)
        core_model.add_component(bus_b)
        core_model.add_connection(bus_a, bus_b, "test1", "test2")

        mapped_connectors = map_connectors(core_model, core_model.type_list(Bus)[0], {"test1": "relabeled_test1"})
        self.assertEqual(
            mapped_connectors,
            {"relabeled_test1": [(core_model.type_list(Bus)[1].uid, ["test2"])]},
        )

    def test_mapping_three_winding_trafo(self) -> None:
        """Test mapping of three winding transformer (HV,MV,LV)."""
        creator = GdfTestComponentCreator(50.0)
        for _ in range(3):
            creator.create_bus()
        creator.create_3w_transformer("threewinding")
        core_model = creator.core_model
        core_model.add_connection(
            core_model.type_list(ThreeWindingTransformer)[0],
            core_model.type_list(Bus)[0],
            "HV",
            "",
        )
        core_model.add_connection(
            core_model.type_list(ThreeWindingTransformer)[0],
            core_model.type_list(Bus)[1],
            "MV",
            "",
        )
        core_model.add_connection(
            core_model.type_list(ThreeWindingTransformer)[0],
            core_model.type_list(Bus)[2],
            "LV",
            "",
        )

        mapped_connectors = map_connectors(
            core_model,
            core_model.type_list(ThreeWindingTransformer)[0],
            {"HV": "relabeled_HV", "MV": "relabeled_MV", "LV": "relabeled_LV"},
        )
        self.assertEqual(
            mapped_connectors,
            {
                "relabeled_HV": [(1, [""])],
                "relabeled_MV": [(2, [""])],
                "relabeled_LV": [(3, [""])],
            },
        )


if __name__ == "__main__":
    unittest.main()
