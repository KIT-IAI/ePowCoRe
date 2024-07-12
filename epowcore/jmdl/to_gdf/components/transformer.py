from dataclasses import dataclass, field
from epowcore.gdf.bus import Bus
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.transformers.transformer import Transformer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.jmdl.jmdl_model import Block
from epowcore.jmdl.utils import get_coordinates


@dataclass(unsafe_hash=True)
class EPowTransformer(Transformer):
    """This class is a direct representation of transformers in JMDL.
    It is only used as an intermediate model to be converted to a universal model."""

    connector_names = ["HV", "LV"]

    # The ratio between the absolute values of the high/to and low/from voltage side
    tap_ratio: float = field(default_factory=float)
    # The phase shift angle in degrees, positive is lagging
    phase_shift: float = field(default_factory=float)
    # The resistance of the transformer in p.u.
    r: float = field(default_factory=float)
    # The reactance of the transformer in p.u.
    x: float = field(default_factory=float)
    # The total line charging susceptance of the transformer in p.u.
    b: float = field(default_factory=float)
    # The long term line rating in MVA
    rate_long_term: float = field(default_factory=float)
    # The short term line rating in MVA
    rate_short_term: float = field(default_factory=float)
    # The emergency rating in MVA
    rate_emergency: float = field(default_factory=float)
    # The minimum angle difference in degrees
    angle_min: float = field(default_factory=float)
    # The maximum angle difference in degrees
    angle_max: float = field(default_factory=float)

    def replace_with_trafo(self, core_model: CoreModel) -> None:
        _, graph = core_model.get_component_by_id(self.uid)
        if graph is None:
            raise ValueError("Component not found!")
        hv_bus = None
        lv_bus = None
        for n in core_model.get_neighbors(self, connector="HV"):
            if isinstance(n, Bus):
                hv_bus = n
                break
        for n in core_model.get_neighbors(self, connector="LV"):
            if isinstance(n, Bus):
                lv_bus = n
                break

        if hv_bus is None or lv_bus is None:
            raise ValueError(f"Could not find connected bus for impedance {self.name}")

        base_mva = core_model.base_mva_fb()
        bm_pu = self.b / self.rate_long_term * base_mva

        trafo = TwoWindingTransformer(
            self.uid,
            self.name,
            self.coords,
            rating=self.rate_long_term,
            rating_short_term=self.rate_short_term,
            rating_emergency=self.rate_emergency,
            voltage_hv=hv_bus.nominal_voltage,
            voltage_lv=lv_bus.nominal_voltage,
            r1pu=self.r / base_mva * self.rate_long_term,
            x1pu=self.x / base_mva * self.rate_long_term,
            pfe_kw=0.0,
            no_load_current=abs(bm_pu) * 100,
            phase_shift_30=round(self.phase_shift / 30),
            tap_ratio=self.tap_ratio,
            angle_min=self.angle_min,
            angle_max=self.angle_max,
        )

        graph.relabel_nodes({self: trafo})


def create_transformer(block: Block, uid: int) -> EPowTransformer:
    trafo_data = block.data.entries_dict["EPowTransformer"].entries_dict
    return EPowTransformer(
        uid,
        block.name,
        get_coordinates(block),
        trafo_data["tapRatio"].value,
        trafo_data["phaseShift"].value,
        trafo_data["R"].value,
        trafo_data["X"].value,
        trafo_data["B"].value,
        trafo_data["rateA"].value,
        trafo_data["rateB"].value,
        trafo_data["rateC"].value,
        trafo_data["angleMin"].value,
        trafo_data["angleMax"].value,
    )
