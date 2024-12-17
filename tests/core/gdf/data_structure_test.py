import copy
import itertools
import json
import os
import unittest
from unittest.mock import patch

from helpers.gdf_component_creator import GdfTestComponentCreator

from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.configuration import Configuration
from epowcore.generic.manipulation.flatten import flatten
from epowcore.generic.singleton import Singleton


class CoreModelTest(unittest.TestCase):
    def setUp(self) -> None:
        Singleton._instances = {}

    # @unittest.skip("tmp")
    def test_corresponding_connector(self) -> None:
        """Test if the corresponding connector is returned correctly."""
        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(3)]
        core_model = creator.core_model
        core_model.add_connection(buses[0], buses[1], "A1", "A2")
        core_model.add_connection(buses[0], buses[2], "B1", "B2")
        core_model.add_connection(buses[1], buses[2], "C1", "C2")
        self.assertEqual(core_model.get_corresponding_connector(buses[0], buses[1], "A1"), "A2")
        self.assertEqual(core_model.get_corresponding_connector(buses[1], buses[0], "A2"), "A1")
        self.assertEqual(core_model.get_corresponding_connector(buses[1], buses[2], "C1"), "C2")
        self.assertEqual(core_model.get_corresponding_connector(buses[2], buses[0], "B2"), "B1")
        self.assertIsNone(core_model.get_corresponding_connector(buses[0], buses[2], "A1"))
        self.assertIsNone(core_model.get_corresponding_connector(buses[2], buses[0], "A1"))

    # @unittest.skip("tmp")
    def test_subsystem(self) -> None:
        """Create subsystem from components, flatten it and check if the subsystem is removed from the core model."""
        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(4)]

        core_model = creator.core_model
        core_model.add_connection(buses[0], buses[1], "A", "A")
        core_model.add_connection(buses[1], buses[2], "B", "B")
        core_model.add_connection(buses[2], buses[3], "C", "C")
        core_model.add_connection(buses[3], buses[0], "D", "D")

        ds_copy = copy.deepcopy(core_model)

        subsystem = Subsystem.from_components(core_model, [buses[3]])

        self.assertEqual(len(core_model.graph.nodes), 4)
        self.assertEqual(len(core_model.graph.edges), 4)
        self.assertEqual(len(subsystem.graph.nodes), 3)
        self.assertEqual(len(subsystem.graph.edges), 2)

        attached = core_model.get_attached_to(buses[0])
        self.assertEqual(len(attached), 2)
        self.assertTrue(subsystem in [x[0] for x in attached])
        self.assertEqual([x for x in attached if x[0] == buses[1]][0][1], ["A"])
        self.assertEqual([x for x in attached if x[0] == subsystem][0][1], ["D"])

        self.assertEqual(core_model.get_connector_names(buses[0]), ["A", "D"])
        self.assertEqual(core_model.get_connection_name(buses[0], buses[1]), ["A"])

        flatten(core_model)
        self.assertEqual(len(core_model.graph.nodes), len(ds_copy.graph.nodes))
        self.assertEqual(len(core_model.graph.edges), len(ds_copy.graph.edges))
        for l, r in itertools.combinations(core_model.graph.nodes, 2):
            self.assertEqual(
                core_model.get_connection_name(l, r),
                ds_copy.get_connection_name(l, r),
            )
            self.assertEqual(
                core_model.get_connection_name(r, l),
                ds_copy.get_connection_name(r, l),
            )

    # @unittest.skip("tmp")
    def test_export_import(self) -> None:
        """Create core model, export it, import it and check if the core model is the same."""
        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(3)]
        tline = creator.create_tline()
        shunt = creator.create_shunt()
        core_model = creator.core_model
        core_model.add_connection(buses[0], shunt)
        subsystem = Subsystem.from_components(core_model, [shunt])
        core_model.add_connection(buses[1], buses[2], "A", "A")
        core_model.add_connection(buses[2], tline, "B", "B")

        dict_export = core_model.export_dict()
        data_str = json.dumps(dict_export, indent=2)
        if not os.path.isdir("./tests/out/gdf"):
            os.mkdir("./tests/out/gdf")
        with open("./tests/out/gdf/core_model_gdf.json", "w", encoding="utf-8") as file:
            file.write(data_str)
        ds_import = CoreModel(base_frequency=50.0).import_dict(dict_export)
        self.assertEqual(len(core_model.graph.nodes), len(ds_import.graph.nodes))
        imported_subsystem = ds_import.get_component_by_id(subsystem.uid)[0]
        self.assertIsNotNone(imported_subsystem)
        self.assertEqual(
            len(subsystem.graph.nodes), len(imported_subsystem.graph.nodes)  # type: ignore
        )
        self.assertEqual(
            len(subsystem.graph.edges), len(imported_subsystem.graph.edges)  # type: ignore
        )
        for component in core_model.graph.nodes:
            self.assertIsNotNone(ds_import.get_component_by_id(component.uid)[0])
        for edge in core_model.graph.edges:
            c1 = ds_import.get_component_by_id(edge[0].uid)[0]
            c2 = ds_import.get_component_by_id(edge[1].uid)[0]
            self.assertTrue(all([c1, c2]))
            self.assertIsNotNone(ds_import.get_connection_name(c1, c2))  # type: ignore

    # @unittest.skip("tmp")
    def test_get_attached_to(self):
        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(4)]

        core_model = creator.core_model
        core_model.add_connection(buses[0], buses[1], "A", "A")
        core_model.add_connection(buses[1], buses[2], "B", "B")
        core_model.add_connection(buses[2], buses[3], "C", "C")
        core_model.add_connection(buses[3], buses[0], "D", "D")

        ds_copy = copy.deepcopy(core_model)

        subsystem = Subsystem.from_components(core_model, [buses[3]])

        self.assertEqual(len(core_model.graph.nodes), 4)
        self.assertEqual(len(core_model.graph.edges), 4)
        self.assertEqual(len(subsystem.graph.nodes), 3)
        self.assertEqual(len(subsystem.graph.edges), 2)

        # print(core_model.get_attached_to(buses[1]))
        # print(core_model.get_attached_to(buses[2]))
        # print(core_model.get_attached_to(buses[3]))

    # TODO: this test doesn't really test get_neighbors
    def test_get_neighbors(self):
        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(4)]

        core_model = creator.core_model
        core_model.add_connection(buses[0], buses[1], "A", "A")
        core_model.add_connection(buses[1], buses[2], "B", "B")
        core_model.add_connection(buses[2], buses[3], "C", "C")

        ds_copy = copy.deepcopy(core_model)

        subsystem_inner = Subsystem.from_components(core_model, [buses[3]])
        subsystem_inner = Subsystem.from_components(core_model, [subsystem_inner])
        subsystem_outer = Subsystem.from_components(core_model, [subsystem_inner, buses[2]])

        self.assertEqual(len(core_model.graph.nodes), 3)
        self.assertEqual(len(core_model.graph.edges), 2)
        self.assertEqual(len(subsystem_inner.graph.nodes), 2)
        self.assertEqual(len(subsystem_inner.graph.edges), 1)

        # print(core_model.get_neighbors(buses[2], follow_links=True))

    def test_get_neighbors_connector(self):
        core_model = CoreModel(base_frequency=50.0)

        bus_a = Bus(1, "Bus A", lf_bus_type=LFBusType.PQ)
        bus_b = Bus(2, "Bus B", lf_bus_type=LFBusType.PQ)

        core_model.add_component(bus_a)
        core_model.add_component(bus_b)

        test_component_creator = GdfTestComponentCreator(50.0)
        tline = test_component_creator.create_tline("TLine")
        tline.uid = 3
        core_model.add_component(tline)
        core_model.add_connection(tline, bus_a, "A")
        core_model.add_connection(tline, bus_b, "B")

        neighbors = core_model.get_neighbors(tline)
        self.assertIn(bus_a, neighbors)
        self.assertIn(bus_b, neighbors)
        self.assertEqual(2, len(neighbors))
        neighbors = core_model.get_neighbors(tline, connector="B")
        self.assertIn(bus_b, neighbors)
        self.assertEqual(1, len(neighbors))

    @patch("epowcore.generic.configuration.Configuration")
    def test_base_mva_fb2(self, mock_config):
        Singleton._instances = {
            Configuration: mock_config,
        }
        mock_config.get_default.return_value = 1000.0
        # self.assertEqual(mock_config.called, True)

        # Configuration().get_default = fake_get_default
        core_model = CoreModel(base_frequency=50.0)

        base_mva = core_model.base_mva_fb()
        self.assertEqual(mock_config.get_default.called, True)
        self.assertEqual(base_mva, 1000.0)


if __name__ == "__main__":
    unittest.main()
