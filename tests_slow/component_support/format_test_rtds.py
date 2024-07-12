from pyapi_rts.api.draft import Draft
from pyapi_rts.api.subsystem import Subsystem

from epowcore.gdf.data_structure import DataStructure
from epowcore.rscad.rscad_converter import RscadConverter
from epowcore.rscad.rscad_export import RscadModel
from tests_slow.component_support.format_test_base import FormatTestBase


class FormatTestRtds(FormatTestBase[RscadModel]):
    def __init__(self, data_structure: DataStructure) -> None:
        super().__init__(RscadConverter(), data_structure)

    def component_count(self) -> int:
        return len(self.model.draft.get_components())

    def contains_subsystem(self) -> bool:
        return any(map(lambda c: isinstance(c, Subsystem), self.model.draft.get_components()))

    def delete(self) -> bool:
        self.model = RscadModel(Draft(), [])
        return True
