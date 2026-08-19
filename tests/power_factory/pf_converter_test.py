
import unittest
from unittest.mock import MagicMock

from helpers.gdf_component_creator import GdfTestComponentCreator

from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.power_factory.from_gdf.components.line import create_line
from epowcore.power_factory.power_factory_converter import PFModel, PowerFactoryConverter


class PFConverterTest(unittest.TestCase):
    """Checks if the minimal model can be imported without errors."""

    def test_minimal_conversion_no_errors(self) -> None:
        """Test if the CoreModel extraction from the Minimal PF model throws errors."""
        converter = PowerFactoryConverter()
        core_model = converter.to_gdf(PFModel("Minimal", "Base", 50.0))

        self.assertEqual(len(core_model.graph.nodes), 8)
        self.assertEqual(len(core_model.graph.edges), 7)

        two_winding_id = core_model.type_list(TwoWindingTransformer)[0].uid

        self.assertTrue(
            any(
                two_winding_id in x[2] and x[2][two_winding_id] == ["HV"]
                for x in core_model.graph.edges.data()
            )
        )

        self.assertTrue(
            any(
                two_winding_id in x[2] and x[2][two_winding_id] == ["LV"]
                for x in core_model.graph.edges.data()
            )
        )

    def test_line_with_missing_connection_is_skipped(self) -> None:
        creator = GdfTestComponentCreator(base_frequency=50.0)

        bus_a = creator.create_bus(name="Bus A")
        line = creator.create_tline(name="Incomplete Line")

        creator.core_model.add_connection(line, bus_a, "A")

        exporter = MagicMock()
        exporter.core_model = creator.core_model
        exporter.pf_grid = MagicMock()

        result = create_line(exporter, line)

        self.assertFalse(result)
        exporter.pf_grid.CreateObject.assert_not_called()


if __name__ == "__main__":
    unittest.main()