from epowcore.gdf.data_structure import DataStructure
from epowcore.jmdl.jmdl_converter import JmdlConverter
from epowcore.jmdl.jmdl_model import JmdlModel
from tests_slow.component_support.format_test_base import FormatTestBase

Model = JmdlModel
"""Content of the eASiMOV model."""


class FormatTestJmdl(FormatTestBase[JmdlModel]):
    def __init__(self, data_structure: DataStructure) -> None:
        super().__init__(JmdlConverter(), data_structure)

    def component_count(self) -> int:
        return len(self.model.root.blocks)  # type: ignore

    def contains_subsystem(self) -> bool:
        return False

    def delete(self) -> bool:
        self.model = None  # type: ignore
        return True
