import unittest

from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.core_model import CoreModel
from epowcore.generic.converter_base import ConverterBase


class DummyConverter(ConverterBase[CoreModel]):
    def _pre_export(self, core_model: CoreModel, name: str) -> CoreModel:
        core_model.add_component(Bus(2, "Added Bus", lf_bus_type=LFBusType.PQ))
        return core_model

    def _export(self, core_model: CoreModel, name: str) -> CoreModel:
        return core_model

    def _import(self, model: CoreModel) -> CoreModel:
        return model


class ConverterBaseTest(unittest.TestCase):
    def test_from_gdf_does_not_modify_original_model(self) -> None:
        core_model = CoreModel(base_frequency=50.0)
        core_model.add_component(Bus(1, "Original Bus", lf_bus_type=LFBusType.PQ))

        converter = DummyConverter()
        converted_model = converter.from_gdf(core_model, "test")

        self.assertEqual(len(core_model.graph.nodes), 1)
        self.assertEqual(len(converted_model.graph.nodes), 2)


if __name__ == "__main__":
    unittest.main()
