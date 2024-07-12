from copy import deepcopy
from epowcore.gdf.bus import Bus
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.load import Load
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.utils import get_connected_bus, get_z_base
from epowcore.generic.logger import Logger
from epowcore.generic.manipulation.flatten import flatten
from epowcore.matpower.matpower_model import (
    BranchDataEntry,
    BusDataEntry,
    GeneratorDataEntry,
    MatpowerModel,
)


def export_matpower(ds: DataStructure) -> MatpowerModel:

    # Matpower does not support subsystems, thus it is easier to work with a flattened model.
    flat_ds = deepcopy(ds)
    flatten(flat_ds)

    base_mva = ds.base_mva_fb()

    buses: dict[int, BusDataEntry] = {}

    bus_list = flat_ds.type_list(Bus)
    bus_list.sort(key=lambda x: x.uid)
    mpc_bus_id = 1

    for b in bus_list:
        buses[b.uid] = BusDataEntry.from_gdf_bus(b, mpc_bus_id)
        mpc_bus_id += 1

    for load in flat_ds.type_list(Load):
        bus: Bus | None = get_connected_bus(flat_ds.graph, load)
        if bus is None:
            Logger.log_to_selected(f"No connected bus found for load {load.name}")
            continue
        buses[bus.uid].demand_p += load.active_power
        buses[bus.uid].demand_q += load.reactive_power

    for shunt in flat_ds.type_list(Shunt):
        bus = get_connected_bus(flat_ds.graph, shunt)
        if bus is None:
            Logger.log_to_selected(f"No connected bus found for shunt {shunt.name}")
            continue
        buses[bus.uid].shunt_g += shunt.p
        buses[bus.uid].shunt_b += shunt.q

    branches: list[BranchDataEntry] = []

    for line in flat_ds.type_list(TLine):
        bus_from = ds.get_neighbors(line, connector="A")[0]
        bus_to = ds.get_neighbors(line, connector="B")[0]

        length = line.length if line.length is not None else 1.0
        r1 = line.r1 * length
        x1 = line.x1 * length
        b1 = line.b1 * length * 1e-6

        branches.append(
            BranchDataEntry(
                from_bus=buses[bus_from.uid].bus_number,
                to_bus=buses[bus_to.uid].bus_number,
                r=r1 / get_z_base(line, ds),
                x=x1 / get_z_base(line, ds),
                b=b1 * get_z_base(line, ds),
                rate_a=line.rating,
                rate_b=line.rating_short_term_fb(),
                rate_c=line.rating_emergency_fb(),
                tap_ratio=0.0,
                ph_shift=0.0,
                angle_min=line.get_fb("angle_min"),
                angle_max=line.get_fb("angle_max"),
                status=1,
            )
        )

    for trafo in flat_ds.type_list(TwoWindingTransformer):
        bus_from = ds.get_neighbors(trafo, connector="HV")[0]
        bus_to = ds.get_neighbors(trafo, connector="LV")[0]

        branches.append(
            BranchDataEntry(
                from_bus=buses[bus_from.uid].bus_number,
                to_bus=buses[bus_to.uid].bus_number,
                r=trafo.r1pu / trafo.rating * base_mva,
                x=trafo.x1pu / trafo.rating * base_mva,
                b=trafo.bm_pu * trafo.rating / base_mva,
                rate_a=trafo.rating,
                rate_b=trafo.rating_short_term_fb(),
                rate_c=trafo.rating_emergency_fb(),
                tap_ratio=trafo.tap_ratio_fb(),
                ph_shift=trafo.phase_shift,
                angle_min=trafo.get_fb("angle_min"),
                angle_max=trafo.get_fb("angle_max"),
                status=1,
            )
        )

    generators: list[GeneratorDataEntry] = []

    for gen in flat_ds.type_list(SynchronousMachine):
        bus = get_connected_bus(flat_ds.graph, gen)
        if bus is None:
            Logger.log_to_selected(f"No connected bus found for generator {gen.name}")
            continue

        buses[bus.uid].voltage_mag = gen.voltage_set_point

        generators.append(
            GeneratorDataEntry(
                bus_number=buses[bus.uid].bus_number,
                pg=gen.active_power,
                qg=gen.reactive_power,
                q_max=gen.q_max,
                q_min=gen.q_min,
                voltage_setpoint=gen.voltage_set_point,
                base_mva=gen.rated_apparent_power,
                status=1,
                p_max=gen.p_max,
                p_min=gen.p_min,
                pc_1=gen.pc1,
                pc_2=gen.pc2,
                qc_min_1=gen.qc1_min,
                qc_max_1=gen.qc1_max,
                qc_min_2=gen.qc2_min,
                qc_max_2=gen.qc2_max,
                ramp_agc=1.0,
                ramp_10=1.0,
                ramp_30=1.0,
                ramp_q=1.0,
                apf=1.0,
            )
        )

    return MatpowerModel(
        base_mva=base_mva, bus=list(buses.values()), gen=generators, branch=branches
    )
