from dataclasses import dataclass, field
import numpy as np
import numpy.typing as npt

from epowcore.gdf.bus import Bus, LFBusType


BUS_TYPE_MAPPING: dict[LFBusType, int] = {
    LFBusType.PQ: 1,
    LFBusType.PV: 2,
    LFBusType.SL: 3,
    LFBusType.ISO: 4,
}


@dataclass(kw_only=True)
class BusDataEntry:
    bus_number: int
    """Bus number (positive integer)"""
    bus_type: LFBusType
    """Loadflow bus type"""
    demand_p: float = 0.0
    """Real power demand [MW]"""
    demand_q: float = 0.0
    """Reactive power demand [Mvar]"""
    shunt_g: float = 0.0
    """Shunt conductance (at V = 1 p.u.) [MW]"""
    shunt_b: float = 0.0
    """Shunt susceptance (at V = 1 p.u.) [Mvar]"""
    area_number: int = 1
    """Area number (positive integer)"""
    voltage_mag: float
    """Voltage magnitude [p.u.]"""
    voltage_angle: float
    """Voltage angle [degrees]"""
    base_kv: float
    """Base voltage [kV]"""
    zone: int = 1
    """Loss zone (positive integer)"""
    voltage_mag_max: float = 1.1
    """Maximum voltage magnitude [p.u.]"""
    voltage_mag_min: float = 0.9
    """Minimum voltage magnitude [p.u.]"""

    @classmethod
    def from_gdf_bus(cls, bus: Bus, uid: int | None = None) -> "BusDataEntry":
        mpc_id = bus.uid if uid is None else uid
        return cls(
            bus_number=mpc_id,
            bus_type=bus.lf_bus_type,
            base_kv=bus.nominal_voltage,
            voltage_mag=1.0,
            voltage_angle=0.0,
        )

    def to_nparray(self) -> npt.ArrayLike:
        return np.array(
            [
                self.bus_number,
                BUS_TYPE_MAPPING[self.bus_type],
                self.demand_p,
                self.demand_q,
                self.shunt_g,
                self.shunt_b,
                self.area_number,
                self.voltage_mag,
                self.voltage_angle,
                self.base_kv,
                self.zone,
                self.voltage_mag_max,
                self.voltage_mag_min,
            ],
            dtype=float,
        )


@dataclass(kw_only=True)
class GeneratorDataEntry:
    bus_number: int
    """Bus number (positive integer)"""
    pg: float
    """Active power output [MW]"""
    qg: float
    """Reactive power output [Mvar]"""
    q_max: float
    """Maximum reactive power output [Mvar]"""
    q_min: float
    """Minimum reactive power output [Mvar]"""
    voltage_setpoint: float
    """Voltage magnitude setpoint [p.u.]"""
    base_mva: float
    """Total MVA base of machine, defaults to base_mva [MVA]"""
    status: float
    """Status > 0 = in-service; otherwise out-of-service"""
    p_max: float
    """Maximum active power output [MW]"""
    p_min: float
    """Minimum active power output [MW]"""
    pc_1: float
    """Lower active power output of PQ capability curve [MW]"""
    pc_2: float
    """Upper active power output of PQ capability curve [MW]"""
    qc_min_1: float
    """Minimum reactive power output at PC1 [Mvar]"""
    qc_max_1: float
    """Maximum reactive power output at PC1 [Mvar]"""
    qc_min_2: float
    """Minimum reactive power output at PC2 [Mvar]"""
    qc_max_2: float
    """Maximum reactive power output at PC2 [Mvar]"""
    ramp_agc: float
    """Ramp rate for load following/AGC [MW/min]"""
    ramp_10: float
    """Ramp rate for 10 minute reserves [MW]"""
    ramp_30: float
    """Ramp rate for 30 minute reserves [MW]"""
    ramp_q: float
    """Ramp rate for reactive power (2s timescale) [Mvar/min]"""
    apf: float
    """Area participation factor"""

    def to_nparray(self) -> npt.ArrayLike:
        return np.array(
            [
                self.bus_number,
                self.pg,
                self.qg,
                self.q_max,
                self.q_min,
                self.voltage_setpoint,
                self.base_mva,
                self.status,
                self.p_max,
                self.p_min,
                self.pc_1,
                self.pc_2,
                self.qc_min_1,
                self.qc_max_1,
                self.qc_min_2,
                self.qc_max_2,
                self.ramp_agc,
                self.ramp_10,
                self.ramp_30,
                self.ramp_q,
                self.apf,
            ],
            dtype=float,
        )


@dataclass(kw_only=True)
class BranchDataEntry:
    from_bus: int
    """'From' bus number"""
    to_bus: int
    """'To' bus number"""
    r: float
    """Resistance [p.u.]"""
    x: float
    """Reactance [p.u.]"""
    b: float
    """Line charging susceptance [p.u.]"""
    rate_a: float
    """Long-term rating, 0 = unlimited [MVA]"""
    rate_b: float
    """Short-term rating, 0 = unlimited [MVA]"""
    rate_c: float
    """Emergency rating, 0 = unlimited [MVA]"""
    tap_ratio: float
    """Transformer off nominal turns ratio; 0 = transmission line"""
    ph_shift: float
    """Transformer phase shift angle, positive = delay [degrees]"""
    status: int
    """Status: 1 = in-service, 0 = out-of-service"""
    angle_min: float
    """Minimum angle difference between buses [degrees]"""
    angle_max: float
    """Maximum angle difference between buses [degrees]"""

    def to_nparray(self) -> npt.ArrayLike:
        return np.array(
            [
                self.from_bus,
                self.to_bus,
                self.r,
                self.x,
                self.b,
                self.rate_a,
                self.rate_b,
                self.rate_c,
                self.tap_ratio,
                self.ph_shift,
                self.status,
                self.angle_min,
                self.angle_max,
            ],
            dtype=float,
        )


@dataclass(kw_only=True)
class MatpowerModel:
    base_mva: float
    version: int = 2
    bus: list[BusDataEntry]
    branch: list[BranchDataEntry]  #  = np.array([], dtype=np.complex128),
    gen: list[GeneratorDataEntry]
    gencost: npt.ArrayLike | None = None
    internal: dict[str, npt.ArrayLike] = field(
        default_factory=lambda: {
            "Ybus": np.array([], dtype=np.complex128),
            "Yf": np.array([], dtype=np.complex128),
            "Yt": np.array([], dtype=np.complex128),
            "branch_is": np.array([], dtype=bool),
            "gen_is": np.array([], dtype=bool),
        }
    )

    def as_dict(self) -> dict:
        return {
            "mpc": {
                "baseMVA": self.base_mva,
                "version": self.version,
                "bus": np.array([b.to_nparray() for b in self.bus], dtype=float),
                "branch": np.array([b.to_nparray() for b in self.branch], dtype=float),
                "gen": np.array([g.to_nparray() for g in self.gen], dtype=float),
                # "gencost": np.array([], dtype=float),
                # "internal": {
                #     "Ybus": np.array([], dtype=np.complex128),
                #     "Yf": np.array([], dtype=np.complex128),
                #     "Yt": np.array([], dtype=np.complex128),
                #     "branch_is": np.array([], dtype=bool),
                #     "gen_is": np.array([], dtype=bool),
                # },
            },
        }
