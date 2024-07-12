from dataclasses import dataclass

from epowcore.gdf.component import Component
from epowcore.gdf.bus import Bus
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.tline import TLine

from epowcore.jmdl.jmdl_model import Block
from epowcore.jmdl.utils import get_coordinates


@dataclass(unsafe_hash=True, kw_only=True)
class EPowLine(Component):
    """This class is a direct representation of transmission lines in JMDL.
    It is only used as an intermediate model to be converted to a universal model.
    """

    connector_names = ["A", "B"]

    r1pu: float
    """Line resistance in p.u."""
    x1pu: float
    """Reactance of the line in p.u."""
    b1pu: float
    """Total line charging susceptance in p.u."""
    rating: float
    """Long term rating of the line in MVA"""
    rating_short_term: float
    """Short term rating of the line in MVA"""
    rating_emergency: float
    """Emergency rating of the line in MVA"""
    angle_min: float
    """Minimum angle difference in degrees"""
    angle_max: float
    """Maximum angle differnce in degrees"""
    parallel_lines: int = 1
    """Number of parallel lines"""

    def replace_with_tline(self, ds: DataStructure) -> None:
        _, graph = ds.get_component_by_id(self.uid)
        if graph is None:
            raise ValueError("Component not found!")
        connected_bus = None
        for n in ds.get_neighbors(self):
            if isinstance(n, Bus):
                connected_bus = n
                break

        if connected_bus is None:
            raise ValueError(f"Could not find connected bus for impedance {self.name}")

        u_base = connected_bus.nominal_voltage
        z_base = u_base**2 / ds.base_mva_fb()

        r1 = self.r1pu * z_base
        x1 = self.x1pu * z_base
        b1 = self.b1pu / (1e-6 * z_base)

        tline = TLine(
            self.uid,
            self.name,
            self.coords,
            r1=r1,
            x1=x1,
            b1=b1,
            rating=self.rating,
            rating_short_term=self.rating_short_term,
            rating_emergency=self.rating_emergency,
            parallel_lines=self.parallel_lines,
            angle_min=self.angle_min,
            angle_max=self.angle_max,
        )

        graph.relabel_nodes({self: tline})


def create_line(block: Block, uid: int) -> EPowLine:
    line_data = block.data.entries_dict["EPowLine"]

    return EPowLine(
        uid,
        block.name,
        coords=get_coordinates(block),
        r1pu=line_data.entries_dict["R"].value,
        x1pu=line_data.entries_dict["X"].value,
        b1pu=line_data.entries_dict["B"].value,
        rating=line_data.entries_dict["rateA"].value,
        rating_short_term=line_data.entries_dict["rateB"].value,
        rating_emergency=line_data.entries_dict["rateC"].value,
        angle_min=line_data.entries_dict["angleMin"].value,
        angle_max=line_data.entries_dict["angleMax"].value,
        parallel_lines=int(line_data.entries_dict["parallelLines"].value),
    )
