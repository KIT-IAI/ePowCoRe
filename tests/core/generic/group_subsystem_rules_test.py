import os
import unittest

from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.logger import Logger
from epowcore.generic.manipulation.group_subsystem_rules import apply_group_subsystem_rules
from epowcore.generic.singleton import Singleton
from tests.helpers.gdf_component_creator import GdfTestComponentCreator

LOG_FILE_PATH = "test.log"


@unittest.skip("Broken tests because of refactoring")
class GroupSubsystemRulesTest(unittest.TestCase):
    """Tests for the grouping subsystem rules."""

    def setUp(self) -> None:
        Singleton._instances = {}

    def tearDown(self) -> None:
        Logger.close_all()
        if os.path.exists(LOG_FILE_PATH):
            os.remove(LOG_FILE_PATH)

    def test_test_rule(self) -> None:
        """Tests the simple rule TestRule matching two connected buses with the port 'GroupTest'"""

        core_model = CoreModel(base_frequency=50.0)
        bus1 = Bus(1, "bus1", lf_bus_type=LFBusType.PQ, nominal_voltage=100.0)
        bus2 = Bus(2, "bus2", lf_bus_type=LFBusType.PQ, nominal_voltage=100.0)
        core_model.add_component(bus1)
        core_model.add_component(bus2)
        core_model.add_connection(bus1, bus2, "GroupTest", "")
        subsystems = apply_group_subsystem_rules(core_model, ["TestRule"])
        self.assertEqual(len(subsystems), 1)  # One subsystem was created
        self.assertEqual(len(core_model.component_list()), 1)

    def test_logging(self) -> None:
        """Tests if the logging works correctly."""

        logger = Logger.new("Test", False)
        core_model = CoreModel(base_frequency=50.0)
        bus1 = Bus(1, "bus1", lf_bus_type=LFBusType.PQ, nominal_voltage=100.0)
        bus2 = Bus(2, "bus2", lf_bus_type=LFBusType.PQ, nominal_voltage=100.0)
        core_model.add_component(bus1)
        core_model.add_component(bus2)
        core_model.add_connection(bus1, bus2, "GroupTest", "")
        apply_group_subsystem_rules(core_model)
        logger.save_to_file(LOG_FILE_PATH)
        with open(LOG_FILE_PATH, "r", encoding="utf8") as f:
            lines = f.read().split("\n")
            self.assertEqual(lines[0], "Test")
            self.assertEqual(lines[2], "Applied rule TestRule and created 1 subsystems")

    def test_multi_subsystems(self) -> None:
        """Tests two core components matching the same rule."""

        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(4)]
        core_model = creator.core_model
        core_model.add_connection(buses[0], buses[1], "GroupTest", "")
        core_model.add_connection(buses[2], buses[3], "GroupTest", "")
        subsystems = apply_group_subsystem_rules(core_model)
        self.assertEqual(len(subsystems), 2)  # Two subsystems have been created
        self.assertEqual(len(core_model.component_list()), 2)

        for i in range(0, 2):
            self.assertEqual(len(subsystems[i].graph.nodes), 2)

    def test_multi_rule(self) -> None:
        """Tests two rules matching the same core components."""

        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(3)]
        core_model = creator.core_model
        core_model.add_connection(buses[0], buses[1], "GroupTest", "")
        core_model.add_connection(buses[0], buses[2], "GroupTest", "")
        subsystems = apply_group_subsystem_rules(core_model)
        self.assertEqual(len(subsystems), 1)
        self.assertEqual(len(subsystems[0].graph.nodes), 3)

    def test_multi_rule2(self) -> None:
        """
        Tests two rules matching with different core components.
        Needs to create one subsystem and ignore the other match.
        """
        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(3)]
        core_model = creator.core_model
        core_model.add_connection(buses[0], buses[1], "GroupTest", "")
        core_model.add_connection(buses[1], buses[2], "GroupTest", "")
        subsystems = apply_group_subsystem_rules(core_model)
        self.assertEqual(len(subsystems), 1)
        self.assertEqual(len(core_model.component_list()), 2)  # One bus and one port
        self.assertEqual(len(subsystems[0].graph.nodes), 3)  # One port and two buses

    def test_priorities(self) -> None:
        """Tests the priority of rules."""

        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(4)]
        core_model = creator.core_model
        core_model.add_connection(buses[0], buses[1], "GroupTest", "")
        core_model.add_connection(buses[1], buses[2], "GroupTest2", "")
        core_model.add_connection(buses[1], buses[3], "GroupTest3", "")
        subsystems = apply_group_subsystem_rules(core_model)
        self.assertEqual(len(subsystems), 1)
        self.assertEqual(len(core_model.component_list()), 1)  # Only one subsystem
        self.assertEqual(len(subsystems[0].graph.nodes), 4)

    def test_include_inner(self) -> None:
        """Tests group rules with the include_inner flag."""

        creator = GdfTestComponentCreator(100.0)
        buses = [creator.create_bus() for _ in range(3)]
        core_model = creator.core_model
        core_model.add_connection(buses[0], buses[1], "GroupTest3", "")
        core_model.add_connection(buses[1], buses[2], "GroupTest3", "")
        subsystems = apply_group_subsystem_rules(core_model)
        self.assertEqual(len(subsystems), 1)
        self.assertEqual(len(core_model.component_list()), 1)
        self.assertEqual(len(subsystems[0].graph.nodes), 3)


if __name__ == "__main__":
    unittest.main()
