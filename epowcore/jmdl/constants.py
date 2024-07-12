from epowcore.gdf.bus import LFBusType


BUS_CLASS_NAME = "edu.kit.iai.easimov.modeler.model.blockdiagram.epower.EPowBus"
GENERATOR_CLASS_NAME = (
    "edu.kit.iai.easimov.modeler.model.blockdiagram.epower.EPowGenerator"
)
LINE_CLASS_NAME = "edu.kit.iai.easimov.modeler.model.blockdiagram.epower.EPowLine"
LOAD_CLASS_NAME = "edu.kit.iai.easimov.modeler.model.blockdiagram.epower.EPowLoad"
TRANSFORMER_CLASS_NAME = (
    "edu.kit.iai.easimov.modeler.model.blockdiagram.epower.EPowTransformer"
)
EXTERNAL_GRID_CLASS_NAME = (
    "edu.kit.iai.easimov.modeler.model.blockdiagram.epower.EPowExternalGrid"
)
SHUNT_CLASS_NAME = "edu.kit.iai.easimov.modeler.model.blockdiagram.epower.EPowShunt"
SWITCH_CLASS_NAME = "edu.kit.iai.easimov.modeler.model.blockdiagram.epower.EPowSwitch"

GDF_JMDL_BUS_TYPE_DICT = {
    LFBusType.PQ: "PQ",
    LFBusType.PV: "PV",
    LFBusType.SL: "REF",
    LFBusType.ISO: "ISOLATED",
}

JMDL_GDF_BUS_TYPE_DICT = {
    "PQ": LFBusType.PQ,
    "PV": LFBusType.PV,
    "REF": LFBusType.SL,
    "ISOLATED": LFBusType.ISO,
}
