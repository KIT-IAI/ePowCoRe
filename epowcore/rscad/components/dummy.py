from dataclasses import dataclass
from epowcore.gdf.component import Component


@dataclass(unsafe_hash=True, kw_only=True)
class Dummy(Component):
    """A dummy component that serves as a placeholder for newly created RSCAD components."""

    rscad_uuid: str
