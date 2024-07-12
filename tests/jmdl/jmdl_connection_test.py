import json
import unittest
from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.singleton import Singleton

from epowcore.jmdl.jmdl_converter import JmdlConverter
from epowcore.jmdl.to_gdf.jmdl_import import JmdlModel

from tests.helpers.gdf_component_creator import GdfTestComponentCreator


class JmdlConnectionTest(unittest.TestCase):
    """Tests if the connections between components are correctly exported to JMDL."""

    def setUp(self) -> None:
        Singleton._instances = {}

    # @unittest.skip("tmp")
    def test_basic_connection(self) -> None:
        """Tests if a basic connection between a generator and a bus is possible."""

        creator = GdfTestComponentCreator(50.0)
        bus_0 = creator.create_bus()
        generator_0 = creator.create_epow_generator()

        core_model = creator.core_model

        core_model.add_connection(bus_0, generator_0)
        jmdl_json = JmdlConverter().from_gdf(core_model, "").to_json()
        imported_jmdl = JmdlModel.from_dict(json.loads(jmdl_json))
        self.assertEqual(imported_jmdl.root.connections[0].start, f"{generator_0.name}.powerOut")
        self.assertEqual(imported_jmdl.root.connections[0].end, f"{bus_0.name}.to_Generator2")

    # @unittest.skip("tmp")
    def test_bus_merge(self) -> None:
        """Test if a case where two buses are connected to each other merges them."""

        creator = GdfTestComponentCreator(50.0)
        bus_0 = creator.create_bus()
        bus_1 = creator.create_bus()
        core_model = creator.core_model
        generator_0 = creator.create_epow_generator()

        core_model.add_connection(bus_0, bus_1)
        core_model.add_connection(bus_1, generator_0, "bus_port", "generator_port")
        jmdl_json = JmdlConverter().from_gdf(core_model, "").to_json()
        imported_jmdl = JmdlModel.from_dict(json.loads(jmdl_json))
        self.assertEqual(len(imported_jmdl.root.blocks), 2)
        self.assertEqual(len(imported_jmdl.root.connections), 1)
        self.assertEqual(imported_jmdl.root.connections[0].start, f"{generator_0.name}.powerOut")
        self.assertEqual(
            imported_jmdl.root.connections[0].end,
            f"{bus_0.name}.to_Generator{generator_0.uid}",
        )

    # @unittest.skip("tmp")
    def test_busbar_insertion(self) -> None:
        """Tests if a busbar is inserted if two non-bus components are directly connected."""
        creator = GdfTestComponentCreator(50.0)
        generator_0 = creator.create_epow_generator()
        shunt_0 = creator.create_shunt()
        core_model = creator.core_model

        core_model.add_connection(generator_0, shunt_0)
        converter = JmdlConverter()
        jmdl_json = converter.from_gdf(core_model, "test_busbar_insertion").to_json()

        imported_jmdl = JmdlModel.from_dict(json.loads(jmdl_json))
        self.assertEqual(imported_jmdl.root.connections[0].start, f"{generator_0.name}.powerOut")
        self.assertEqual(
            imported_jmdl.root.connections[0].end,
            f"BusBar_3.to_Generator{generator_0.uid}",
        )
        self.assertEqual(imported_jmdl.root.connections[1].start, f"{shunt_0.name}.powerIn")
        self.assertEqual(imported_jmdl.root.connections[1].end, f"BusBar_3.to_Shunt{shunt_0.uid}")

    # @unittest.skip("tmp")
    def test_busbar_insertion_2(self) -> None:
        """Tests the insertion of a busbar with more than two non-bus components connected."""

        creator = GdfTestComponentCreator(50.0)
        generator_0 = creator.create_epow_generator()
        shunt_0 = creator.create_shunt()
        core_model = creator.core_model

        core_model.add_connection(generator_0, shunt_0)
        jmdl_json = JmdlConverter().from_gdf(core_model, "test_busbar_insertion").to_json()
        imported_jmdl = JmdlModel.from_dict(json.loads(jmdl_json))
        self.assertEqual(imported_jmdl.root.connections[0].start, f"{generator_0.name}.powerOut")
        self.assertEqual(
            imported_jmdl.root.connections[0].end,
            f"BusBar_3.to_Generator{generator_0.uid}",
        )
        self.assertEqual(imported_jmdl.root.connections[1].start, f"{shunt_0.name}.powerIn")
        self.assertEqual(imported_jmdl.root.connections[1].end, f"BusBar_3.to_Shunt{shunt_0.uid}")
        with open("tests/out/test_busbar_insertion.jmdl", "w", encoding="utf8") as f:
            f.write(jmdl_json)

    # @unittest.skip("tmp")
    def test_multiple_connections(self) -> None:
        """Test multiple connections between two components.

        In this example, both ends of a transmission line are connected to the same subsystem.
        The JMDL model is valid and the load flow calculation converges.
        In the core model, there should be two top-level components (line and subsystem)
        and two connections between those components.
        Inside the subsystem, there should be two Ports connecting the line to the internal buses.
        """
        with open("tests/models/jmdl/double_connection.jmdl", "r", encoding="utf8") as file:
            json_data = json.loads(file.read())
        jmdl_model = JmdlModel.from_dict(json_data)
        self.assertEqual(len(jmdl_model.root.blocks), 1)
        self.assertEqual(len(jmdl_model.root.super_blocks), 1)
        self.assertEqual(len(jmdl_model.root.connections), 2)

        jmdl_converter = JmdlConverter()
        core_model = jmdl_converter.to_gdf(jmdl_model)
        for e in core_model.graph.edges:
            print(core_model.graph.edges.data(e))
        print("---")

        self.assertEqual(len(core_model.graph.nodes), 2)
        for n in core_model.graph.nodes:
            print(n)
        print("---")
        subsys = core_model.type_list(Subsystem)[0]
        for n in subsys.graph.nodes:
            print(n)


if __name__ == "__main__":
    unittest.main()
