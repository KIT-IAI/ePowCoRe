import copy
import os
import json
import unittest
from epowcore.gdf.load import Load
from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.manipulation.flatten import flatten
from epowcore.generic.singleton import Singleton
from epowcore.jmdl.jmdl_converter import JmdlConverter
from epowcore.jmdl.to_gdf.jmdl_import import JmdlModel


class JmdlTest(unittest.TestCase):
    """Tests the JMDL Import and Export functionality"""

    def compare_dict(self, dict1: dict, dict2: dict, path: str = "") -> bool:
        """Compares two dictionaries.

        :param dict1: The first dictionary
        :type dict1: dict
        :param dict2: The second dictionary
        :type dict2: dict
        :param path: The path to the current element
        :type path: str
        :return: True if the dictionaries are equal, False otherwise
        :rtype: bool
        """
        for key in dict1:
            if key not in dict2:
                print(f"{path}.{key} not in dict2")
                return False
            else:
                if isinstance(dict1[key], dict):
                    if not self.compare_dict(dict1[key], dict2[key], f"{path}.{key}"):
                        return False
                else:
                    if dict1[key] != dict2[key]:
                        print(f"{path}.{key} does not match")
                        return False
        return True

    def setUp(self) -> None:
        Singleton._instances = {}

    # @unittest.skip("tmp")
    def test_import(self) -> None:
        """Tests the import of JMDL files"""
        json_data = None
        with open("tests/models/jmdl/model.jmdl", "r", encoding="utf8") as file:
            json_data = json.loads(file.read())
        root = JmdlModel.from_dict(json_data)
        json_out = root.as_dict()
        # Create directory if it does not exist
        if not os.path.exists("tests/out"):
            os.makedirs("tests/out")
        with open("tests/out/out.jmdl", "w", encoding="utf8") as file:
            file.write(json.dumps(json_out, indent=4))
        self.assertTrue(self.compare_dict(json_data, json_out))
        self.assertTrue(self.compare_dict(json_out, json_data))
        self.assertEqual(root.base_frequency, 50)

    # @unittest.skip("tmp")
    def test_with_super_block(self) -> None:
        """Tests the import of a super block to a Subsystem."""
        json_data = None
        with open("tests/models/jmdl/with_super_block.jmdl", "r", encoding="utf8") as file:
            json_data = json.loads(file.read())
        root = JmdlModel.from_dict(json_data)
        jmdl_converter = JmdlConverter()
        ds = jmdl_converter.to_gdf(root)

        load = next((x for x in ds.graph.nodes if isinstance(x, Load)), None)
        self.assertEqual(load.coords, (1.0, 2.0))  # type: ignore
        self.assertEqual(len(ds.graph.nodes), 2)
        self.assertEqual(len(ds.graph.edges), 1)

        sub = ds.type_list(Subsystem)[0]
        self.assertEqual(len(sub.graph.nodes), 2)
        self.assertEqual(len(sub.graph.edges), 1)

        jmdl_json = jmdl_converter.from_gdf(ds, "with_super_block_out").to_json()
        with open("tests/out/with_super_block_out.jmdl", "w", encoding="utf8") as file:
            file.write(jmdl_json)

    # @unittest.skip("tmp")
    def test_minimal_super_block(self) -> None:
        """Tests the import of a super block to a Subsystem."""
        json_data = None
        with open("tests/models/jmdl/minimal_subsystem.jmdl", "r", encoding="utf8") as file:
            json_data = json.loads(file.read())
        root = JmdlModel.from_dict(json_data)
        jmdl_converter = JmdlConverter()
        ds = jmdl_converter.to_gdf(root)

        print(json.dumps(ds.export_dict(), indent=2))
        print("\n\n#######################################\n\n")

        flatten(ds)
        print(json.dumps(ds.export_dict(), indent=2))

    def test_minimal_super_block2(self) -> None:
        """Tests the import of a super block to a Subsystem."""
        json_data = None
        with open("tests/models/jmdl/minimal_subsystem_double.jmdl", "r", encoding="utf8") as file:
            json_data = json.loads(file.read())
        root = JmdlModel.from_dict(json_data)
        jmdl_converter = JmdlConverter()
        ds = jmdl_converter.to_gdf(root)
        ds_original = copy.deepcopy(ds)

        # print(json.dumps(ds.export_dict(), indent=2))

        # print("\n\n#######################################\n\n")
        # ds_flattened = flatten(ds)
        # print(json.dumps(ds_flattened.export_dict(), indent=2))

        jmdl_converter = JmdlConverter()
        jmdl_json = jmdl_converter.from_gdf(ds_original, "minimal_subsystem_double_out").to_json()
        with open("tests/out/minimal_subsystem_double_out.jmdl", "w", encoding="utf8") as file:
            file.write(jmdl_json)


if __name__ == "__main__":
    unittest.main()
