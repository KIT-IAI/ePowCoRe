from abc import ABC, abstractmethod

from pyapi_rts.api.component import Component as RSCADComponent

from epowcore.gdf.component import Component as GDFComponent


class RSCADComponentBuilder(ABC):
    """Base class for RSCAD component builders."""

    @classmethod
    @abstractmethod
    def get_connection_point(cls, component: RSCADComponent, connection: str) -> tuple[int, int]:
        """Get the connection point of a component."""

    @classmethod
    @abstractmethod
    def create(cls, component: GDFComponent, base_frequency: float) -> RSCADComponent:
        """Create a RSCAD component from a GDF component."""

    @staticmethod
    def sanitize_string(name: str) -> str:
        """Remove special characters from a string to make it a valid RSCAD component name."""
        return (
            name.replace(" ", "")
            .replace("-", "")
            .replace("/", "")
            .replace("_", "")
            .replace("(", "")
            .replace(")", "")
        )
