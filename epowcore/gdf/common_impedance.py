from dataclasses import dataclass, field

from .component import Component


@dataclass(unsafe_hash=True, kw_only=True)
class CommonImpedance(Component):
    """The Common Impedance is a per unit impedance model including an ideal transformer.
    The main usage is for branches used for network reduction."""

    connector_names = ["A", "B"]

    sn_mva: float = field(default_factory=float)
    """The rated apparent power in MVA."""
    r_pu: float = field(default_factory=float)
    """Real part of positive sequence impedance from A to B [p.u.]"""
    x_pu: float = field(default_factory=float)
    """Imaginary part of positive sequence impedance from A to B [p.u.]"""
    r_pu_ba: float | None = None
    """Real part of positive sequence impedance from B to A [p.u.]"""
    x_pu_ba: float | None = None
    """Imaginary part of positive sequence impedance from B to A [p.u.]"""
    g_pu_a: float | None = None
    """Real part of admittance at terminal A [p.u.]"""
    b_pu_a: float | None = None
    """Imaginary part of admittance at terminal A [p.u.]"""
    g_pu_b: float | None = None
    """Real part of admittance at terminal B [p.u.]"""
    b_pu_b: float | None = None
    """Imaginary part of admittance at terminal B [p.u.]"""
    phase_shift: float = 0.0
    """Phase shift from terminal A to B [deg]"""
