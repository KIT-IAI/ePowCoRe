from math import pi
import matlab.engine
from epowcore.gdf.bus import Bus
from epowcore.gdf.common_impedance import CommonImpedance
from epowcore.gdf.data_structure import DataStructure
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.shared import SimscapeBlockType

BLOCK_TYPE = SimscapeBlockType.COMMON_IMPEDANCE


def create_common_impedance(
    eng: matlab.engine.MatlabEngine,
    impedance: CommonImpedance,
    data_structure: DataStructure,
    model_name: str,
) -> SimscapeBlock:
    neighbors = data_structure.get_neighbors(impedance, connector="B")
    if not neighbors or not isinstance(neighbors[0], Bus):
        raise ValueError(f"Could not find connected bus for impedance {impedance.name}")
    bus_b: Bus = neighbors[0]

    neighbors = data_structure.get_neighbors(impedance, connector="A")
    if not neighbors or not isinstance(neighbors[0], Bus):
        raise ValueError(f"Could not find connected bus for impedance {impedance.name}")
    bus_a: Bus = neighbors[0]

    u_base = bus_b.nominal_voltage
    z_base = u_base**2 / impedance.sn_mva
    y_base = 1 / z_base
    w = 2 * pi * data_structure.base_frequency
    x = impedance.x_pu * z_base

    block_name = f"{model_name}/{impedance.name}"
    eng.add_block(BLOCK_TYPE.value, block_name, nargout=0)

    eng.set_param(block_name, "R", f"{impedance.r_pu * z_base}", nargout=0)
    eng.set_param(block_name, "Ui", f"{bus_a.nominal_voltage*1e3}", nargout=0)
    eng.set_param(block_name, "Uj", f"{bus_b.nominal_voltage*1e3}", nargout=0)

    phase_shift = int(impedance.phase_shift % 360)
    # see Simscape Specialized Power Systems Three-Phase Transformer documentation 
    # for conversion guide
    if phase_shift == 30:
        # -> -30 = Yd1
        eng.set_param(block_name, "Winding1Connection", "Y", nargout=0)
        eng.set_param(block_name, "Winding2Connection", "Delta (D1)", nargout=0)
    elif phase_shift == 60:
        # -> -60 = Dd2
        eng.set_param(block_name, "Winding1Connection", "Delta (D11)", nargout=0)
        eng.set_param(block_name, "Winding2Connection", "Delta (D1)", nargout=0)
    elif phase_shift == 150:
        # -> -150 = Yd5
        eng.set_param(block_name, "Winding1Connection", "Y", nargout=0)
        eng.set_param(block_name, "Winding2Connection", "Delta (D1)", nargout=0)
        eng.set_param(block_name, "ConnectionVariant", "bca", nargout=0)
    elif phase_shift == 210:
        # -> +150 = Yd7
        eng.set_param(block_name, "Winding1Connection", "Y", nargout=0)
        eng.set_param(block_name, "Winding2Connection", "Delta (D11)", nargout=0)
        eng.set_param(block_name, "ConnectionVariant", "bca", nargout=0)
    elif phase_shift == 300:
        # -> +60 = Dd10
        eng.set_param(block_name, "Winding1Connection", "Delta (D1)", nargout=0)
        eng.set_param(block_name, "Winding2Connection", "Delta (D11)", nargout=0)
    elif phase_shift == 330:
        # -> +30 = Yd11
        eng.set_param(block_name, "Winding1Connection", "Y", nargout=0)
        eng.set_param(block_name, "Winding2Connection", "Delta (D11)", nargout=0)

    l = x / w
    eng.set_param(block_name, "L", f"{l}", nargout=0)
    eng.set_param(block_name, "C", "0.0", nargout=0)

    if impedance.g_pu_a is not None and impedance.b_pu_a is not None:
        g = impedance.g_pu_a * y_base
        b = impedance.b_pu_a * y_base

        if g == 0 and b == 0:
            eng.set_param(block_name, "Ri", "Inf", nargout=0)
            eng.set_param(block_name, "Li", "Inf", nargout=0)
        else:
            r = 1 / g
            l = -1 / (b * w)
            eng.set_param(block_name, "Ri", f"{r}", nargout=0)
            eng.set_param(block_name, "Li", f"{l}", nargout=0)

    if impedance.g_pu_b is not None and impedance.b_pu_b is not None:
        g = impedance.g_pu_b * y_base
        b = impedance.b_pu_b * y_base

        if g == 0 and b == 0:
            eng.set_param(block_name, "Rj", "Inf", nargout=0)
            eng.set_param(block_name, "Lj", "Inf", nargout=0)
        else:
            r = 1 / g
            l = -1 / (b * w)
            eng.set_param(block_name, "Rj", f"{r}", nargout=0)
            eng.set_param(block_name, "Lj", f"{l}", nargout=0)

    return SimscapeBlock(block_name, BLOCK_TYPE)
