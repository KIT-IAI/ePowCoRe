from epowcore.gdf.data_structure import DataStructure
from epowcore.power_factory.power_factory_converter import PowerFactoryConverter
from tests_slow.component_support.format_test_base import FormatTestBase


class FormatTestPf(FormatTestBase[str]):
    def __init__(self, data_structure: DataStructure) -> None:
        super().__init__(PowerFactoryConverter(), data_structure)

    def component_count(self) -> int:
        raise NotImplementedError()

    def contains_subsystem(self) -> bool:
        return False

    def delete(self) -> bool:
        self.model = ""
        return True
