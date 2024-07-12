import copy
import unittest
from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.transformers import TwoWindingTransformer
from epowcore.gdf.data_structure import DataStructure

from epowcore.gdf.subsystem import Subsystem
from epowcore.gdf.transformers.transformer import WindingConfig
from epowcore.generic.manipulation.flatten import flatten
from tests.helpers.gdf_component_creator import GdfTestComponentCreator


class SubsystemPortsTest(unittest.TestCase):
    """Test the implementation of cross-subsystem connections via Ports.
    Ensures that the result of flattened models is equal to original models without subsystems.
    """

    # @unittest.skip("tmp")
    def test_one_port_connection(self) -> None:
        """One connection between two buses. One bus gets moved into a new subsystem."""

        ds = DataStructure(base_frequency=50.0)
        bus_a = Bus(1, "Bus A", lf_bus_type=LFBusType.PQ)
        bus_b = Bus(2, "Bus B", lf_bus_type=LFBusType.PQ)
        ds.add_component(bus_a)
        ds.add_component(bus_b)
        ds.add_connection(bus_a, bus_b, "A1", "B1")

        ds_original = copy.deepcopy(ds)
        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        subsystem = Subsystem.from_components(ds, [bus_a])

        self.assertEqual(len(ds.graph.nodes), 2)
        self.assertEqual(len(ds.graph.edges), 1)
        self.assertEqual(len(subsystem.graph.nodes), 2)
        self.assertEqual(len(subsystem.graph.edges), 1)

        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        flatten(ds)
        self.assertEqual(ds.export_dict(), ds_original.export_dict())
        # print(json.dumps(ds_flattened.export_dict(), indent=2))

    # @unittest.skip("tmp")
    def test_two_port_connection(self) -> None:
        """Two connections between two lines. One line gets moved into a new subsystem."""
        creator = GdfTestComponentCreator(50.0)
        tlines = [creator.create_tline() for _ in range(2)]

        ds = creator.data_structure
        ds.add_connection(tlines[0], tlines[1], ["A", "B"], ["A", "B"])

        ds_original = copy.deepcopy(ds)
        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        subsystem = Subsystem.from_components(ds, [tlines[0]])

        self.assertEqual(len(ds.graph.nodes), 2)
        self.assertEqual(len(ds.graph.edges), 1)
        self.assertEqual(len(subsystem.graph.nodes), 2)
        self.assertEqual(len(subsystem.graph.edges), 1)

        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        flatten(ds)
        self.assertEqual(ds.export_dict(), ds_original.export_dict())
        # print(json.dumps(ds_flattened.export_dict(), indent=2))

    # @unittest.skip("tmp")
    def test_line_bus_connection(self) -> None:
        """One connection between a line and two buses. Line gets moved into a new subsystem."""
        creator = GdfTestComponentCreator(50.0)
        tline = creator.create_tline()

        ds = creator.data_structure
        bus_a = Bus(2, "Bus A", lf_bus_type=LFBusType.PQ)
        bus_b = Bus(3, "Bus B", lf_bus_type=LFBusType.PQ)
        ds.add_component(bus_a)
        ds.add_component(bus_b)
        ds.add_connection(tline, bus_a, ["A"], ["A"])
        ds.add_connection(tline, bus_b, ["B"], ["B"])

        ds_original = copy.deepcopy(ds)
        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        subsystem = Subsystem.from_components(ds, [tline])

        self.assertEqual(len(ds.graph.nodes), 3)
        self.assertEqual(len(ds.graph.edges), 2)
        self.assertEqual(len(subsystem.graph.nodes), 3)
        self.assertEqual(len(subsystem.graph.edges), 2)

        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        flatten(ds)
        self.assertEqual(ds.export_dict(), ds_original.export_dict())
        # print(json.dumps(ds_flattened.export_dict(), indent=2))

    # @unittest.skip("tmp")
    def test_line_bus_connection2(self) -> None:
        """One connection between a line and two buses. Buses get moved into a new subsystem."""
        creator = GdfTestComponentCreator(50.0)
        tline = creator.create_tline()

        ds = creator.data_structure
        bus_a = Bus(2, "Bus A", lf_bus_type=LFBusType.PQ)
        bus_b = Bus(3, "Bus B", lf_bus_type=LFBusType.PQ)
        ds.add_component(bus_a)
        ds.add_component(bus_b)
        ds.add_connection(tline, bus_a, ["LA"], ["A"])
        ds.add_connection(tline, bus_b, ["LB"], ["B"])

        ds_original = copy.deepcopy(ds)
        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        subsystem = Subsystem.from_components(ds, [bus_a, bus_b])

        self.assertEqual(len(ds.graph.nodes), 2)
        self.assertEqual(len(ds.graph.edges), 1)
        self.assertEqual(len(subsystem.graph.nodes), 3)
        self.assertEqual(len(subsystem.graph.edges), 2)

        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        flatten(ds)
        self.assertEqual(ds.export_dict(), ds_original.export_dict())
        # print(json.dumps(ds_flattened.export_dict(), indent=2))

    def test_line_bus_connection3(self) -> None:
        """One connection between a line and two buses. Buses get moved into separate new subsystems."""
        creator = GdfTestComponentCreator(50.0)
        tline = creator.create_tline()

        ds = creator.data_structure
        bus_a = Bus(2, "Bus A", lf_bus_type=LFBusType.PQ)
        bus_b = Bus(3, "Bus B", lf_bus_type=LFBusType.PQ)
        ds.add_component(bus_a)
        ds.add_component(bus_b)
        ds.add_connection(tline, bus_a, ["LA"], ["A"])
        ds.add_connection(tline, bus_b, ["LB"], ["B"])

        ds_original = copy.deepcopy(ds)
        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        subsystem1 = Subsystem.from_components(ds, [bus_a])
        subsystem2 = Subsystem.from_components(ds, [bus_b])

        self.assertEqual(len(ds.graph.nodes), 3)
        self.assertEqual(len(ds.graph.edges), 2)
        self.assertEqual(len(subsystem1.graph.nodes), 2)
        self.assertEqual(len(subsystem1.graph.edges), 1)
        self.assertEqual(len(subsystem2.graph.nodes), 2)
        self.assertEqual(len(subsystem2.graph.edges), 1)

        # print(json.dumps(ds.export_dict(), indent=2))
        # print("\n\n#######################################\n\n")

        flatten(ds)
        self.assertEqual(ds.export_dict(), ds_original.export_dict())
        # print(json.dumps(ds_flattened.export_dict(), indent=2))

    @unittest.skip("only for exploration")
    def test_subsystem_variations_for_exploration(self) -> None:
        """One connection between two buses. One bus gets moved into a new subsystem."""

        ds = DataStructure(base_frequency=50.0)
        bus_hv = Bus(1, "Bus HV", lf_bus_type=LFBusType.PQ)
        bus_lv = Bus(3, "Bus LV", lf_bus_type=LFBusType.PQ)
        trafo = TwoWindingTransformer(
            2,
            "Transformer",
            rating=100.0,
            voltage_hv=50.0,
            voltage_lv=100.0,
            r1pu=0.2,
            pfe_kw=0.2,
            no_load_current=0.5,
            x1pu=0.5,
            connection_type_hv=WindingConfig.YN,
            connection_type_lv=WindingConfig.YN,
            phase_shift_30=0,
            tap_changer_voltage=0.5,
            tap_min=0,
            tap_max=2,
            tap_neutral=0,
            tap_initial=1,
        )
        ds.add_component(bus_hv)
        ds.add_component(bus_lv)
        ds.add_component(trafo)
        ds.add_connection(trafo, bus_hv, "HV", "")
        ds.add_connection(trafo, bus_lv, "LV", "")

        subsys = Subsystem.from_components(ds, [trafo])

        edge_data = ds.graph.edges.data(bus_lv)
        print(edge_data)

        print("---")

        edge_data = subsys.graph.edges.data(trafo)
        print(edge_data)


if __name__ == "__main__":
    unittest.main()
