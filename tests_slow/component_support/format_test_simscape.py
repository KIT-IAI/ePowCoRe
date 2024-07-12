import os

import matlab.engine

from epowcore.gdf.data_structure import DataStructure
from epowcore.simscape.simscape_converter import SimscapeConverter
from epowcore.simscape.shared import SimscapeBlockType
from tests_slow.component_support.format_test_base import FormatTestBase


class FormatTestSimscape(FormatTestBase):
    def __init__(self, data_structure: DataStructure) -> None:
        converter = SimscapeConverter()
        super().__init__(converter, data_structure)
        self.eng = converter.eng

    def component_count(self) -> int:
        block_list = self.eng.getfullname(self.eng.Simulink.findBlocks(self.model))
        if isinstance(block_list, str):
            return 1
        if not isinstance(block_list, (list, matlab.double)):
            raise TypeError("Unexpected type for block_list")
        return len(block_list)  # type: ignore

    def contains_subsystem(self) -> bool:
        block_list = self.eng.getfullname(self.eng.Simulink.findBlocks(self.model))
        if isinstance(block_list, str):
            block_list = [block_list]
        if not isinstance(block_list, (list, matlab.double)):
            raise TypeError("Unexpected type for block_list")
        for block in block_list:  # type: ignore
            if self.eng.get_param(block, "BlockType") in (
                SimscapeBlockType.SUBSYSTEM.value,
                SimscapeBlockType.VARIANT_SUBSYSTEM.value,
            ):
                return True
        return False

    def delete(self) -> bool:
        # Delete file in current directory with the same name as the model
        res = os.path.exists(self.model + ".slx")
        if res:
            os.remove(self.model + ".slx")
        self.model = ""
        return res
