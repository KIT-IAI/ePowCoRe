from dataclasses import dataclass, field
from epowcore.gdf.data_structure import DataStructure

from epowcore.gdf.shunt import Shunt

from .component import Component
from .load import Load


# The attributes are never changed after being insterted into a structure requiring hashes
@dataclass(unsafe_hash=True, kw_only=True)
class Ward(Component):
    """This class represents a Ward equivalent.
    It consists of a constant impedance load and constant PQ load and generation."""

    p_load: float = field(default_factory=float)
    """The active power of the load. The unit is MW."""
    q_load: float = field(default_factory=float)
    """The reactive power of the load. The unit is Mvar."""
    p_gen: float = field(default_factory=float)
    """The active power of the generator. The unit is MW."""
    q_gen: float = field(default_factory=float)
    """The reactive power of the generator. The unit is Mvar."""
    p_zload: float = field(default_factory=float)
    """The active power of the constant impedance load. The unit is MW."""
    q_zload: float = field(default_factory=float)
    """The reactive power of the constant impedance load. The unit is Mvar."""

    def replace_with_load_and_shunt(self, data_structure: DataStructure) -> None:
        """Replaces the Ward equivalent with a Load and a Shunt component in the graph.

        :param data_structure: The data structure to replace the ward in.
        :type data_structure: DataStructure
        """
        new_id = data_structure.get_valid_id()
        load = Load(
            new_id,
            f"{self.name}-Load",
            None,
            active_power=self.p_load - self.p_gen,
            reactive_power=self.q_load - self.q_gen,
        )
        shunt = Shunt(
            new_id + 1,
            f"{self.name}-Shunt",
            None,
            q=self.q_zload,
            p=self.p_zload,
        )
        bus = list(data_structure.graph.neighbors(self))[0]

        data_structure.add_component(load)
        data_structure.add_component(shunt)
        data_structure.add_connection(bus, load)
        data_structure.add_connection(bus, shunt)

        data_structure.remove_component(self)
