from dataclasses import dataclass, field

from epowcore.gdf.bus import Bus, LFBusType
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer

from .transformer import Transformer, WindingConfig


@dataclass(unsafe_hash=True, kw_only=True)
class ThreeWindingTransformer(Transformer):
    """This class represents a three-phase transformer with three windings.

    Note that the impedances between two sides in p.u.
    refer to the minimum rating of the two sides.
    Otherwise, p.u. values are based on the HV rating."""

    connector_names = ["HV", "MV", "LV"]

    rating_hv: float = field(default_factory=float)
    """High voltage rating of the transformer [MVA]"""
    rating_mv: float = field(default_factory=float)
    """Medium voltage rating of the transformer [MVA]"""
    rating_lv: float = field(default_factory=float)
    """Low voltage rating of the transformer [MVA]"""

    voltage_hv: float = field(default_factory=float)
    """Voltage on the high voltage side [kV]"""
    voltage_mv: float = field(default_factory=float)
    """Voltage on the medium voltage side [kV]"""
    voltage_lv: float = field(default_factory=float)
    """Voltage on the low voltage side [kV]"""

    x1_hm: float = field(default_factory=float)
    """Positive sequence reactance between HV and MV [p.u.]"""
    x1_ml: float = field(default_factory=float)
    """Positive sequence reactance between MV and LV [p.u.]"""
    x1_lh: float = field(default_factory=float)
    """Positive sequence reactance between LV and HV [p.u.]"""

    r1_hm: float = field(default_factory=float)
    """Positive sequence resistance (copper losses) between HV and MV [p.u.]"""
    r1_ml: float = field(default_factory=float)
    """Positive sequence resistance (copper losses) between MV and LV [p.u.]"""
    r1_lh: float = field(default_factory=float)
    """Positive sequence resistance (copper losses) between LV and HV [p.u.]"""

    pfe_kw: float = field(default_factory=float)
    """No load losses (iron losses) of the transformer [kW]"""
    no_load_current: float = field(default_factory=float)
    """Magnetic no load current of the transformer [%]"""

    connection_type_hv: WindingConfig
    """The type of connection on the high voltage side."""
    connection_type_mv: WindingConfig
    """The type of connection on the middle voltage side."""
    connection_type_lv: WindingConfig
    """The type of connection on the low voltage side."""
    phase_shift_30_hv: int
    """Phase shift for primary winding [30 deg]"""
    phase_shift_30_mv: int
    """Phase shift for secondary winding [30 deg]"""
    phase_shift_30_lv: int
    """Phase shift for tertiary winding [30 deg]"""

    @property
    def pfe_pu(self) -> float:
        """No load losses (iron losses) of the transformer [p.u.]"""
        return self.pfe_kw / self.rating_hv / 1000

    def replace_with_two_winding_transformers(self, core_model: CoreModel) -> None:
        """Creates three two winding transformers and their auxiliary bus from a three winding transformer.

        The new auxiliary bus is connected to the LV side of each of the three new transformers.

        :param core_model: The core model that contains this three winding transformer.
        :return: None
        """
        # Create auxilary bus
        auxilary_bus = Bus(
            self.uid,  # Id
            self.name + "aux",  # Name
            self.coords,
            nominal_voltage=1.0,  # Voltage: set to 1 kV for auxiliary bus
            lf_bus_type=LFBusType.PQ,  # BusType
        )
        # Create three two winding transformers
        two_winding_transformers = []
        new_id = core_model.get_valid_id()

        x1_h, x1_m, x1_l = _calculate_impedances(
            (self.x1_hm, self.x1_ml, self.x1_lh),
            (self.rating_hv, self.rating_mv, self.rating_lv),
        )
        r1_h, r1_m, r1_l = _calculate_impedances(
            (self.r1_hm, self.r1_ml, self.r1_lh),
            (self.rating_hv, self.rating_mv, self.rating_lv),
        )

        # T1
        two_winding_transformers.append(
            TwoWindingTransformer(
                new_id,
                self.name + "H",
                self.coords,
                rating=self.rating_hv,
                voltage_hv=self.voltage_hv,
                voltage_lv=1.0,
                r1pu=r1_h,
                x1pu=x1_h,
                pfe_kw=self.pfe_kw,
                no_load_current=self.no_load_current,
                connection_type_hv=self.connection_type_hv,
                connection_type_lv=WindingConfig.YN,
                phase_shift_30=self.phase_shift_30_hv,
            )
        )
        # T2
        two_winding_transformers.append(
            TwoWindingTransformer(
                new_id + 1,  # Id
                self.name + "M",  # Name
                self.coords,
                rating=self.rating_mv,
                voltage_hv=self.voltage_mv,
                voltage_lv=1.0,
                r1pu=r1_m,
                x1pu=x1_m,
                pfe_kw=0,
                no_load_current=0,
                connection_type_hv=self.connection_type_mv,
                connection_type_lv=WindingConfig.YN,
                phase_shift_30=self.phase_shift_30_mv,
            )
        )
        # T3
        two_winding_transformers.append(
            TwoWindingTransformer(
                new_id + 2,  # Id
                self.name + "L",  # Name
                self.coords,
                rating=self.rating_lv,
                voltage_hv=self.voltage_lv,
                voltage_lv=1.0,
                r1pu=r1_l,
                x1pu=x1_l,
                pfe_kw=0,
                no_load_current=0,
                connection_type_hv=self.connection_type_lv,
                connection_type_lv=WindingConfig.YN,
                phase_shift_30=self.phase_shift_30_lv,
            )
        )

        # Add elements to core model
        neighbors = list(core_model.graph.neighbors(self))
        core_model.graph.remove_node(self)

        # Add connections to graph
        core_model.add_connection(auxilary_bus, two_winding_transformers[0], "", "LV")
        core_model.add_connection(auxilary_bus, two_winding_transformers[1], "", "LV")
        core_model.add_connection(auxilary_bus, two_winding_transformers[2], "", "LV")

        for i in range(min(len(neighbors), 3)):
            core_model.add_connection(two_winding_transformers[i], neighbors[i], "HV", "")


def _calculate_impedances(
    impedances: tuple[float, float, float], ratings: tuple[float, float, float]
) -> tuple[float, float, float]:
    """Calculate equivalent impedances for two winding transformers."""
    z_hm, z_ml, z_lh = impedances
    rating_h, rating_m, rating_l = ratings

    # impedance values are based on minimum rating of the two involved sides
    # this brings all impedances to the same (synthetic) 1 MVA rating
    z_hm = z_hm / min(rating_h, rating_m)
    z_ml = z_ml / min(rating_l, rating_m)
    z_lh = z_lh / min(rating_h, rating_l)

    # calculate individual impedances according to:
    # A. Boyajian, “Progress in Three-Circuit Theory,”
    # Transactions of the American Institute of Electrical Engineers,
    # vol. 52, no. 3, pp. 914–917, Sep. 1933, doi: 10.1109/T-AIEE.1933.5056420.

    z_h = (z_hm + z_lh - z_ml) / 2
    z_m = (z_hm + z_ml - z_lh) / 2
    z_l = (z_ml + z_lh - z_hm) / 2

    # transform back to correct base rating for each transformer
    return z_h * rating_h, z_m * rating_m, z_l * rating_l
