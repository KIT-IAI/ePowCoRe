from dataclasses import dataclass

from .generator import Generator


@dataclass(unsafe_hash=True, kw_only=True)
class SynchronousMachine(Generator):
    """A synchronous machine."""

    rated_apparent_power: float
    """Rated apparent power in MVA"""
    rated_active_power: float
    """Rated active power of the generator in MW."""
    rated_voltage: float
    """Rated voltage of the generator in kV."""

    active_power: float
    """Active power output of the generator in MW."""
    reactive_power: float
    """Reactive power output of the generator in Mvar."""
    voltage_set_point: float
    """Voltage setpoint the generator tries to hold."""

    inertia_constant: float
    """Inertia constant H in seconds."""
    zero_sequence_resistance: float
    """Zero sequence resistance in p.u."""
    zero_sequence_reactance: float
    """Zero sequence reactance in p.u."""
    stator_leakage_reactance: float
    """Stator leakage reactance in p.u."""
    stator_resistance: float
    """Stator resistance in p.u."""
    synchronous_reactance_x: float
    """Unsaturated transient reactance in p.u."""
    transient_reactance_x: float
    """Unsaturated transient reactance in p.u."""
    subtransient_reactance_x: float
    """Unsaturated subtransient reactance in p.u."""
    synchronous_reactance_q: float
    """Unsaturated transient reactance in p.u."""
    transient_reactance_q: float
    """Unsaturated transient reactance in p.u."""
    subtransient_reactance_q: float
    """Unsaturated subtransient reactance in p.u."""

    tds0: float | None = None
    """Short-circuit transient time constant d-axis in s."""
    tqs0: float | None = None
    """Short-circuit transient time constant q-axis in s."""
    tdss0: float | None = None
    """Short-circuit subtransient time constant d-axis in s."""
    tqss0: float | None = None
    """Short-circuit subtransient time constant q-axis in s."""

    p_min: float
    """Minimum active power output in MW."""
    p_max: float
    """Maximum active power output in MW."""
    q_min: float
    """Minimum reactive power output in Mvar."""
    q_max: float
    """Maximum reactive power output in Mvar."""
    # Capability
    pc1: float
    """Lower active power output of the PQ capability curve in MW."""
    pc2: float
    """Upper active power output of the PQ capability curve in MW."""
    qc1_min: float
    """Minimum reactive power output at PC1 in Mvar."""
    qc1_max: float
    """Maximum reactive power output at PC1 in Mvar."""
    qc2_min: float
    """Minimum reactive power output at PC2 in Mvar."""
    qc2_max: float
    """Maximum reactive power output at PC2 in Mvar."""
