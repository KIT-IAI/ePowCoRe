from dataclasses import dataclass, field
from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.impedance import Impedance

from epowcore.gdf.shunt import Shunt
from epowcore.gdf.voltage_source import VoltageSource

from .bus import Bus, LFBusType
from .load import Load
from .ward import Ward


@dataclass(unsafe_hash=True, kw_only=True)
class ExtendedWard(Ward):
    """This class represents a Ward equivalent.
    It consists of a constant impedance load and constant PQ load and generation."""

    u_setp: float = field(default_factory=float)
    """The voltage setpoint for the internal voltage source in pu."""
    r_ext: float = field(default_factory=float)
    """The internal resistance of the internal voltage source in Ohm."""
    x_ext: float = field(default_factory=float)
    """The internal reactance of the internal voltage source in Ohm."""

    def replace_with_load_shunt_vsource(
        self,
        core_model: CoreModel,
        base_mva: float = 100.0,
    ) -> None:
        """Replaces the Ward equivalent with a Load, a Shunt component, and a VoltageSource in the graph.

        :param core_model: The core model to replace the ward in.
        :type core_model: CoreModel
        """
        bus: Component = next(core_model.graph.neighbors(self))
        if not isinstance(bus, Bus):
            raise TypeError(f"Expected {self} to be connected to a Bus, but got {bus}.")

        new_id = core_model.get_valid_id()
        load = Load(
            new_id,
            f"{self.name}-Load",
            bus.coords,
            active_power=self.p_load - self.p_gen,
            reactive_power=self.q_load - self.q_gen,
        )
        shunt = Shunt(
            new_id + 1,
            f"{self.name}-Shunt",
            bus.coords,
            q=self.q_zload,
            p=self.p_zload,
        )
        int_bus = Bus(
            new_id + 2,
            f"{self.name}-IntBus",
            bus.coords,
            nominal_voltage=bus.nominal_voltage,
            lf_bus_type=LFBusType.PV,
        )
        z_base = bus.nominal_voltage**2 / base_mva
        int_impedance = Impedance(
            new_id + 3,
            f"{self.name}-IntImpedance",
            bus.coords,
            sn_mva=base_mva,
            r_pu=self.r_ext / z_base,
            x_pu=self.x_ext / z_base,
        )
        int_vsource = VoltageSource(
            new_id + 4,
            f"{self.name}-Gen",
            bus.coords,
            u_setp=self.u_setp,
            phi_setp=0.0,
            r_pu=1e-8,
            x_pu=1e-8,
        )

        core_model.graph.remove_node(self)
        core_model.graph.add_edge(bus, load)
        core_model.graph.add_edge(bus, shunt)
        core_model.graph.add_edge(bus, int_impedance)
        core_model.graph.add_edge(int_impedance, int_bus)
        core_model.graph.add_edge(int_bus, int_vsource)
