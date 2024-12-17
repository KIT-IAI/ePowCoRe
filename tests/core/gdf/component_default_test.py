import os
import unittest

from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.switch import Switch
from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import Platform
from epowcore.generic.logger import Logger
from epowcore.jmdl.jmdl_converter import JmdlConverter

LOG_FILE_PATH = "test.log"


class ComponentDefaultTest(unittest.TestCase):
    """Test the default value mechanism for components."""

    # @unittest.skip("tmp")
    def test_default_values(self) -> None:
        """Test the basic default value mechanics."""
        switch = Switch(1, "Switch 1", closed=True, rate_b=120.0)

        logger = Logger.new(origin="Default Test")

        rate_a = switch.get_default("rate_a", Platform.JMDL)
        self.assertEqual(rate_a, 100.0)
        self.assertEqual(len(logger.entries), 1)

        Configuration().default_platform = Platform.JMDL

        rate_b = switch.rate_b
        self.assertEqual(rate_b, 120.0)
        self.assertEqual(len(logger.entries), 1)

        rate_b = switch.get_fb("rate_b")
        self.assertEqual(rate_b, 120.0)
        self.assertEqual(len(logger.entries), 1)

        rate_c = switch.get_fb("rate_c")
        self.assertEqual(rate_c, 110.0)
        self.assertEqual(len(logger.entries), 2)

    def test_default_value_export(self) -> None:
        """Test the usage of default values when exporting to JMDL."""

        core_model = CoreModel(base_frequency=50.0)
        switch1 = Switch(1, "Switch 1", closed=True, rate_a=10, rate_b=12, rate_c=15)
        switch2 = Switch(2, "Switch 2", closed=True)
        bus1 = Bus(3, "Bus 1", lf_bus_type=LFBusType.PQ, nominal_voltage=20.0)
        bus2 = Bus(4, "Bus 2", lf_bus_type=LFBusType.PQ, nominal_voltage=20.0)
        bus3 = Bus(5, "Bus 3", lf_bus_type=LFBusType.PQ, nominal_voltage=20.0)

        core_model.add_component(switch1)
        core_model.add_component(switch2)
        core_model.add_component(bus1)
        core_model.add_component(bus2)
        core_model.add_component(bus3)
        core_model.add_connection(bus1, switch1)
        core_model.add_connection(bus2, switch1)
        core_model.add_connection(bus2, switch2)
        core_model.add_connection(bus3, switch2)

        jmdl_converter = JmdlConverter()
        converted = jmdl_converter.from_gdf(core_model, "test", log_path=LOG_FILE_PATH)

        jmdl_switch1 = converted.root.blocks[0].data.entries_dict["EPowSwitch"]
        jmdl_switch2 = converted.root.blocks[1].data.entries_dict["EPowSwitch"]

        self.assertEqual(jmdl_switch1.entries_dict["rateA"].value, 10)
        self.assertEqual(jmdl_switch1.entries_dict["rateB"].value, 12)
        self.assertEqual(jmdl_switch1.entries_dict["rateC"].value, 15)
        self.assertEqual(jmdl_switch2.entries_dict["rateA"].value, 100)
        self.assertEqual(jmdl_switch2.entries_dict["rateB"].value, 105)
        self.assertEqual(jmdl_switch2.entries_dict["rateC"].value, 110)

        self.assertEqual(jmdl_switch2.entries_dict["inService"].value, True)

        with open(LOG_FILE_PATH, "r", encoding="utf8") as log_file:
            lines = log_file.readlines()
            # one line for the header
            # one each for in_service
            self.assertEqual(len(lines), 6)

        with open("tests/out/test_default_value_export.jmdl", "w", encoding="utf-8") as file:
            file.write(converted.to_json())

    def tearDown(self) -> None:
        Logger.close_all()
        if os.path.exists(LOG_FILE_PATH):
            os.remove(LOG_FILE_PATH)


if __name__ == "__main__":
    unittest.main()
