from dataclasses import dataclass, field
from epowcore.gdf.bus import Bus
from epowcore.gdf.core_model import CoreModel

from epowcore.gdf.tline import TLine
from epowcore.gdf.utils import get_connected_bus
from epowcore.generic.constants import Platform

from .component import Component


@dataclass(unsafe_hash=True, kw_only=True)
class Impedance(Component):
    """A series impedance."""

    connector_names = ["A", "B"]

    sn_mva: float = field(default_factory=float)
    """The rated apparent power in MVA."""
    r_pu: float = field(default_factory=float)
    """Real part of positive sequence impedance from A to B in pu."""
    x_pu: float = field(default_factory=float)
    """Imaginary part of positive sequence impedance from A to B in pu."""
    r_pu_ba: float | None = None
    """Real part of positive sequence impedance from B to A in pu."""
    x_pu_ba: float | None = None
    """Imaginary part of positive sequence impedance from B to A in pu."""

    def replace_with_line(
        self, core_model: CoreModel, platform: Platform | None = None
    ) -> None:
        """Replaces the Impedance with a TLine component in the graph.

        :param core_model: The CoreModel to replace this component in.
        :type core_model: CoreModel
        """
        connected_bus: Bus | None = get_connected_bus(core_model.graph, self)
        if connected_bus is None:
            raise ValueError(f"Could not find connected bus for impedance {self.name}")
        bus: Bus = connected_bus
        u_base = bus.nominal_voltage
        z_base = u_base**2 / self.sn_mva

        b1 = self.get_default("b1_line", platform)
        b0 = self.get_default("b0_line", platform)

        if b1 is None or b0 is None:
            raise ValueError("No default values found for Impedance to TLine conversion!")

        line = TLine(
            core_model.get_valid_id(),
            f"{self.name}-Line",
            bus.coords,
            length=1.0,
            r1=self.r_pu * z_base,
            x1=self.x_pu * z_base,
            b1=b1,
            r0=self.r_pu * z_base * 3,
            x0=self.x_pu * z_base * 3,
            b0=b0,
            rating=self.sn_mva,
        )
        buses = list(core_model.graph.neighbors(self))

        core_model.add_component(line)
        core_model.add_connection(buses[0], line)
        core_model.add_connection(buses[1], line)
        core_model.remove_component(self)
