from epowcore.gdf.core_model import CoreModel
from epowcore.power_factory.power_factory_converter import PowerFactoryConverter
from tests_slow.component_support.format_test_base import FormatTestBase


class FormatTestPf(FormatTestBase[str]):
    def __init__(self, core_model: CoreModel) -> None:
        super().__init__(PowerFactoryConverter(), core_model)

    def component_count(self) -> int:
        raise NotImplementedError()

    def contains_subsystem(self) -> bool:
        return False

    def delete(self) -> bool:
        self.model = ""
        return True
