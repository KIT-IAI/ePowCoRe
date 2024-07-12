import unittest
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.power_factory.power_factory_converter import PFModel, PowerFactoryConverter


class PFConverterTest(unittest.TestCase):
    """Checks if the minimal model can be imported without errors."""

    def test_minimal_conversion_no_errors(self) -> None:
        """Test if the DataStructure extraction from the Minimal PF model throws errors."""
        converter = PowerFactoryConverter()
        ds = converter.to_gdf(PFModel("Minimal", "Base", 50.0))
        self.assertEqual(len(ds.graph.nodes), 8)
        self.assertEqual(len(ds.graph.edges), 7)
        two_winding_id = ds.type_list(TwoWindingTransformer)[0].uid
        self.assertTrue(
            any(
                two_winding_id in x[2] and x[2][two_winding_id] == ["HV"]
                for x in ds.graph.edges.data()
            )
        )
        self.assertTrue(
            any(
                two_winding_id in x[2] and x[2][two_winding_id] == ["LV"]
                for x in ds.graph.edges.data()
            )
        )


if __name__ == "__main__":
    unittest.main()
