# Connection Points are placed on OFFSET + N * STEP_SIZE
from typing import Union
from pyapi_rts.generated.rtdsPSS1Adef import rtdsPSS1Adef
from pyapi_rts.generated.rtdsPTIST1def import rtdsPTIST1def
from pyapi_rts.generated.rtdsIEEET1def import rtdsIEEET1def
from pyapi_rts.generated.rtdsEXST1Adef import rtdsEXST1Adef

GRID_OFFSET = 16
GRID_STEP_SIZE = 32

CONNECTION_DICTIONARY: dict[str, list[tuple[str, str]]] = {
    "_rtds_PTIST1.def": [
        ("W", "W"),
        ("VS", "Vs"),
        ("Pe", "PMACH"),
    ],
    "_rtds_PSS1A.def": [
        ("W", "W"),
        ("VS", "Vs"),
    ],
    "_rtds_IEEEG1.def": [
        ("W", "W"),
        ("OUT1", "Tm"),
    ],
    "_rtds_IEEET1.def": [
        ("OUT", "Ef"),
        ("VPU", "Vpu"),
        ("VS", "Vs"),
    ],
    "_rtds_EXST1A.def": [
        ("OUT", "Ef"),
        ("VPU", "Vpu"),
        ("VS", "Vs"),
        ("IFLD", "If"),
    ],
    "lf_rtds_sharc_sld_MACV31": [
        ("EFLDN", "Ef"),
        ("TMECH", "Tm"),
        ("GWO", "W"),
        ("VTMPU", "Vpu"),
        ("IFLDN", "If"),
    ],
}
"""A dictionary that contains port mappings for RSCAD components.

RSCAD component type names are used as keys with lists of mappings as the values.
Mappings are string tuples with the RSCAD port name and our unified port name that
matches corresponding ports of different components.

Example:
The `OUT1` port of the IEEEG1 governor should be connected to the `TMECH` port of the generator.
Thus, both ports are mapped to a common `Tm` string that is used to create a common wire label.
"""

RSCADPSS = Union[rtdsPTIST1def, rtdsPSS1Adef]
"""Type alias that contains all supported RSCAD PSS components in a Union."""
RSCADExciters = Union[rtdsIEEET1def, rtdsEXST1Adef]
"""Type alias that contains all supported RSCAD exciter components in a Union."""
