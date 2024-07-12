from enum import Enum
from typing import Type
import unittest

from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.transformer import WindingConfig
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from tests_slow.component_support.format_test_jmdl import FormatTestJmdl
from tests_slow.component_support.format_test_rtds import FormatTestRtds
from tests_slow.component_support.format_test_simscape import FormatTestSimscape


class ComponentTestResult(Enum):
    """The result of a component test."""

    NO = 0
    YES = 1
    CONTAINS_SUBSYSTEM = 2
    MULTI_COMPONENT = 3

# @unittest.skip("tmp")
class ComponentExportTest(unittest.TestCase):
    """Test the export of components to GDF."""

    def test_export(self) -> None:
        """For all component suppored by GDF, test that the component can be exported and to what level."""

        components = [
            Bus(1, "bus1", None, lf_bus_type=LFBusType.PQ),
            TwoWindingTransformer(
                2,
                "two_w_g1",
                rating=100.0,
                voltage_hv=100.0,
                voltage_lv=100.0,
                r1pu=0.2,
                pfe_kw=0.1,
                no_load_current=0.1,
                x1pu=0.1,
                connection_type_hv=WindingConfig.YN,
                connection_type_lv=WindingConfig.YN,
                tap_changer_voltage=1.0,
                tap_min=1,
                tap_max=1,
                tap_neutral=1,
                tap_initial=1,
                phase_shift_30=0,
            ),
            ThreeWindingTransformer(
                3,
                "Trafo1",
                rating_hv=100.0,
                rating_mv=50.0,
                rating_lv=20.0,
                voltage_hv=100.0,
                voltage_mv=50.0,
                voltage_lv=10.0,
                x1_hm=0.5,
                x1_ml=0.5,
                x1_lh=0.5,
                r1_hm=0.5,
                r1_ml=0.5,
                r1_lh=0.5,
                pfe_kw=0.5,
                no_load_current=0.0,
                connection_type_hv=WindingConfig.YN,
                connection_type_mv=WindingConfig.YN,
                connection_type_lv=WindingConfig.YN,
                phase_shift_30_lv=0,
                phase_shift_30_mv=0,
                phase_shift_30_hv=0,
            ),
            Shunt(5, "shunt_0", None, 10.0, 10.0),
        ]
        testformats: list[Type] = [FormatTestJmdl, FormatTestRtds, FormatTestSimscape]
        results = {}

        for component in components:
            r = []
            for testformat in testformats:
                ds = DataStructure(base_frequency=50.0)
                ds.add_component(component)
                export_model = testformat(ds)
                component_count = export_model.component_count()
                contains_subsystem = export_model.contains_subsystem()
                if component_count == 1 and not contains_subsystem:
                    r.append(ComponentTestResult.YES)
                elif component_count > 1 and not contains_subsystem:
                    r.append(ComponentTestResult.MULTI_COMPONENT)
                elif contains_subsystem:
                    r.append(ComponentTestResult.CONTAINS_SUBSYSTEM)
                else:
                    r.append(ComponentTestResult.NO)
                export_model.delete()
            results[component] = r
        for component, result in results.items():
            print(type(component).__name__, result)


if __name__ == "__main__":
    unittest.main()
