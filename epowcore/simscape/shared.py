from enum import Enum


class SimscapeBlockType(Enum):
    """Mapping to the library paths that are used to create Simscape components."""

    BUS = "sps_lib/Utilities/Load Flow Bus"
    SYNC_MACHINE = "sps_lib/Electrical Machines/Synchronous Machine pu Standard"
    LOAD = "sps_lib/Passives/Three-Phase Series RLC Load"
    PI_SECTION = "sps_lib/Power Grid Elements/Three-Phase PI Section Line"
    TW_TRANSFORMER = "sps_lib/Power Grid Elements/Three-Phase Transformer (Two Windings)"
    THW_TRANSFORMER = "sps_lib/Power Grid Elements/Three-Phase Transformer (Three Windings)"
    IEEEST1A = "sps_lib/Electrical Machines/Synchronous Machine Control/ST1A Excitation System"
    SEXS = "customLib/SEXS 1"
    IEEEPSS1A = "ee_sl_lib/SM Control/SM PSS1A"
    IEEEPSS2A = "ee_sl_lib/SM Control/SM PSS2C"
    GAST = "customLib/GAST 1"
    HYGOV = "customLib/Hydro1 1"
    IEEEG1 = "ee_sl_lib/Turbine-Governors/Governor Type 1"
    VI_MEASUREMENT = "sps_lib/Sensors and Measurements/Three-Phase V-I Measurement"
    SCOPE = "simulink/Commonly Used Blocks/Scope"
    SUBSYSTEM = "built-in/Subsystem"
    VARIANT_SUBSYSTEM = "simulink/Ports & Subsystems/Variant Subsystem"
    POWERGUI = "sps_lib/powergui"
    INPORT = "simulink/Ports & Subsystems/In1"
    OUTPORT = "simulink/Ports & Subsystems/Out1"
    IMPEDANCE = "sps_lib/Passives/Three-Phase Series RLC Branch"
    COMMON_IMPEDANCE = "customLib/Common Impedance RL 1"
    STATIC_GEN = "sps_lib/Passives/Three-Phase Dynamic Load"
