import json
import unittest

from epowcore.gdf import Bus
from epowcore.gdf.generators.generator import Generator
from epowcore.gdf.transformers.transformer import Transformer
from epowcore.jmdl.jmdl_converter import JmdlConverter
from epowcore.jmdl.jmdl_model import JmdlModel
from tests.helpers.gdf_component_creator import GdfTestComponentCreator
from tests.helpers.jmdl_diff import diff


class JmdlGenericConversionTest(unittest.TestCase):
    """Test the conversion between the generic format and the JMDL format."""

    def test_jmdl_to_generic(self) -> None:
        """Test the conversion from JMDL to generic format."""

        json_data = None
        with open("tests/models/jmdl/model.jmdl", "r", encoding="utf8") as file:
            json_data = json.loads(file.read())
        converter = JmdlConverter()
        structure = converter.to_gdf(JmdlModel.from_dict(json_data))
        self.assertEqual(len(structure.type_list(Bus)), 9)
        self.assertEqual(len(structure.type_list(Generator)), 3)

    def test_jmdl_to_generic_to_jmdl(self) -> None:
        """Test the conversion from JMDL to generic format and back to JMDL."""
        json_str = ""
        with open("tests/models/jmdl/model.jmdl", "r", encoding="utf8") as file:
            json_str = file.read()
        converter = JmdlConverter()
        structure = converter.json_to_gdf(json_str)
        jmdl_2 = converter.from_gdf(structure, "jmdl").to_json()
        with open("tests/out/model_2.jmdl", "w", encoding="utf8") as file:
            file.write(jmdl_2)
        self.assertTrue(diff("tests/models/jmdl/model.jmdl", "tests/out/model_2.jmdl"))

    def test_jmdl_two_winding_trafo(self) -> None:
        """Tests the JMDL import of a two winding transformer."""
        creator = GdfTestComponentCreator()
        bus_list = [creator.create_bus() for _ in range(3)]
        trafo1 = creator.create_3w_transformer()
        data_struct = creator.data_structure

        data_struct.add_connection(bus_list[0], trafo1)
        data_struct.add_connection(bus_list[1], trafo1)
        data_struct.add_connection(bus_list[2], trafo1)

        # Note: transform() converts the ThreeWindingTransformer to three TwoWindingTransformers

        converter = JmdlConverter()
        jmdl_export = converter.from_gdf(data_struct, "jmdl").to_json()

        with open("tests/out/three_winding.jmdl", "w", encoding="utf8") as file:
            file.write(jmdl_export)

        # Convert to 3 two winding transformers
        trafo1.replace_with_two_winding_transformers(data_struct)

        self.assertEqual(len(data_struct.type_list(Transformer)), 3)
        self.assertEqual(len(data_struct.graph.nodes), 7)
        self.assertEqual(len(data_struct.graph.edges), 6)

        jmdl_export = converter.from_gdf(data_struct, "jmdl").to_json()
        with open("tests/out/3_two_winding.jmdl", "w", encoding="utf8") as file:
            file.write(jmdl_export)


if __name__ == "__main__":
    unittest.main()
