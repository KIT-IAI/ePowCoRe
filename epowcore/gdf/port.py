from dataclasses import dataclass, field
from epowcore.gdf.component import Component


@dataclass(unsafe_hash=True)
class Port(Component):
    """A surrogate component to enable connections between components in subsystems and higher level components."""

    connection_component: int = field(default_factory=int)
