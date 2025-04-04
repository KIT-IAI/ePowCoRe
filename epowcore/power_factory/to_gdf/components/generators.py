import powerfactory as pf

from epowcore.gdf.generators.static_generator import StaticGenerator
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.power_factory.utils import get_coords


def create_synchronous_machine(
    gen: pf.DataObject, uid: int, use_load_flow: bool = False
) -> SynchronousMachine:
    """Create a synchronous machine from a PowerFactory object."""

    rated_active_power = gen.pgini
    rated_apparent_power = gen.typ_id.sgn
    rated_voltage = gen.typ_id.ugn

    if use_load_flow:
        active_power = gen.GetAttribute("m:P:bus1")
        reactive_power = gen.GetAttribute("m:Q:bus1")
    else:
        active_power = gen.pgini
        reactive_power = gen.qgini

    # number of parallel machines
    gnum = gen.ngnum

    return SynchronousMachine(
        uid,
        gen.loc_name,
        get_coords(gen),
        rated_apparent_power=rated_apparent_power * gnum,
        rated_active_power=rated_active_power * gnum,
        rated_voltage=rated_voltage,
        active_power=active_power * gnum,
        reactive_power=reactive_power * gnum,
        voltage_set_point=gen.usetp,
        inertia_constant=gen.typ_id.h,
        zero_sequence_resistance=gen.typ_id.r0sy,
        zero_sequence_reactance=gen.typ_id.x0sy,
        stator_leakage_reactance=gen.typ_id.xl,
        stator_resistance=gen.typ_id.rstr,
        synchronous_reactance_x=gen.typ_id.xd,
        transient_reactance_x=gen.typ_id.xds,
        subtransient_reactance_x=gen.typ_id.xdss,
        synchronous_reactance_q=gen.typ_id.xq,
        transient_reactance_q=gen.typ_id.xqs,
        subtransient_reactance_q=gen.typ_id.xqss,
        tds0=gen.typ_id.tds0,
        tqs0=gen.typ_id.tqs0,
        tdss0=gen.typ_id.tdss0,
        tqss0=gen.typ_id.tqss0,
        p_min=gen.Pmin_uc * gnum,
        p_max=gen.P_max * gnum,
        q_min=gen.typ_id.Q_min * gnum,
        q_max=gen.typ_id.Q_max * gnum,
        pc1=gen.Pmin_uc * gnum,
        pc2=gen.Pmax_uc * gnum,
        qc1_min=gen.cQ_min * gnum,
        qc1_max=gen.cQ_max * gnum,
        qc2_min=gen.cQ_min * gnum,
        qc2_max=gen.cQ_max * gnum,
    )


def create_static_generator(gen: pf.DataObject, uid: int, use_load_flow: bool = False) -> StaticGenerator:
    """Create a static generator from a PowerFactory object."""

    rated_active_power = gen.pgini
    rated_apparent_power = gen.sgn

    if use_load_flow:
        active_power = gen.GetAttribute("m:P:bus1")
        reactive_power = gen.GetAttribute("m:Q:bus1")
    else:
        active_power = gen.pgini
        reactive_power = gen.qgini

    # number of parallel machines
    gnum = gen.ngnum

    return StaticGenerator(
        uid,
        gen.loc_name,
        get_coords(gen),
        rated_apparent_power=rated_apparent_power * gnum,
        rated_active_power=rated_active_power * gnum,
        active_power=active_power * gnum,
        reactive_power=reactive_power * gnum,
        voltage_set_point=gen.usetp,
        p_min=gen.Pmin_uc * gnum,
        p_max=gen.P_max * gnum,
        q_min=gen.cQ_min * gnum,
        q_max=gen.cQ_max * gnum,
    )
