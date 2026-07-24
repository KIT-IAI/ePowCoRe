from dataclasses import dataclass, field

from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.tline import TLine
from epowcore.generic.constants import Platform

from .component import Component


@dataclass(unsafe_hash=True, kw_only=True)
class Switch(Component):
    """A switch."""

    closed: bool = field()
    """If set to true, the switch connects."""
    in_service: bool | None = None
    """If set to true, switch has no failure."""
    rate_a: float | None = None
    """Long term rating [MVA]."""
    rate_b: float | None = None
    """Short term rating [MVA]."""
    rate_c: float | None = None
    """Emergency rating [MVA]."""

    def replace_with_line_if_closed(self, core_model: CoreModel, platform: Platform) -> None:
        if not self.closed:
            core_model.remove_component(self)
            return None

        line = TLine(
            uid=core_model.get_valid_id(),
            name=self.name + "_tline",
            length=None,
            r1=self.get_default(attr="tline_r1", platform=platform),
            x1=self.get_default(attr="tline_x1", platform=platform),
            b1=self.get_default(attr="tline_b1", platform=platform),
            rating=(
                self.rate_a
                if not self.rate_a is None
                else self.get_default(attr="tline_rating", platform=platform)
            ),
            rating_short_term=self.rate_b,
            rating_emergency=self.rate_c,
        )

        buses = list(core_model.graph.neighbors(self))

        core_model.add_component(line)
        core_model.add_connection(buses[0], line)
        core_model.add_connection(buses[1], line)
