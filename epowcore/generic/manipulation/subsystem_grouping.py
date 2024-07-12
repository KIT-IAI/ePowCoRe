from abc import ABC, abstractmethod

from epowcore.gdf.component import Component
from epowcore.gdf.data_structure import DataStructure


class SubsystemGrouping(ABC):
    """Base class for subsystem groupings."""

    name: str

    @classmethod
    @abstractmethod
    def check_match(cls, core_component: Component, ds: DataStructure) -> list[Component] | None:
        """Check if the [core_component] matches the requirements of this grouping.
        If yes, return the list of components that should be moved to a new subsystem.

        :param core_component: The core component of the grouping structure. Does not have to be part of the new subsystem!
        :type core_component: Component
        :param ds: The data structure to work on.
        :type ds: DataStructure
        :return: The list of components that should be grouped together in a new subsystem.
        :rtype: list[Component] | None
        """

    @classmethod
    def get_name(
        cls, core_component: Component, ds: DataStructure, components: list[Component]
    ) -> str:
        """Get a name for the new subsystem based on the [core_component],
        [components] and the data structure.

        :param core_component: The core component of the grouping.
        :type core_component: Component
        :param ds: The data structure to work on.
        :type ds: DataStructure
        :param components: The components included in the new subsystem.
        :type components: list[Component]
        :return: The name of the new subsystem.
        :rtype: str
        """
        return f"Subsystem: {core_component.name}"
