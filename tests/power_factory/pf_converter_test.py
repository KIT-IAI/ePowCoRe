import unittest

from epowcore.gdf.exciters.exciter import Exciter
from epowcore.gdf.governors.governor import Governor
from epowcore.gdf.power_system_stabilizers.power_system_stabilizer import PowerSystemStabilizer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
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

        for controller_type in (Exciter, Governor, PowerSystemStabilizer):
            controller = core_model.type_list(controller_type)[0]
            self.assertTrue(
                any(
                    controller.uid in edge_data and edge_data[controller.uid] == ["In", "Out"]
                    for _, _, edge_data in core_model.graph.edges.data()
                )
            )


if __name__ == "__main__":
    unittest.main()
