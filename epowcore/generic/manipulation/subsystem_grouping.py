from abc import ABC, abstractmethod

from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel


class SubsystemGrouping(ABC):
    """Base class for subsystem groupings."""

    name: str

    @classmethod
    @abstractmethod
    def check_match(cls, core_component: Component, core_model: CoreModel) -> list[Component] | None:
        """Check if the [core_component] matches the requirements of this grouping.
        If yes, return the list of components that should be moved to a new subsystem.

        :param core_component: The core component of the grouping structure. Does not have to be part of the new subsystem!
        :type core_component: Component
        :param core_model: The core model to work on.
        :type core_model: CoreModel
        :return: The list of components that should be grouped together in a new subsystem.
        :rtype: list[Component] | None
        """

    @classmethod
    def get_name(
        cls, core_component: Component, core_model: CoreModel, components: list[Component]
    ) -> str:
        """Get a name for the new subsystem based on the [core_component],
        [components] and the core model.

        :param core_component: The core component of the grouping.
        :type core_component: Component
        :param core_model: The core model to work on.
        :type core_model: CoreModel
        :param components: The components included in the new subsystem.
        :type components: list[Component]
        :return: The name of the new subsystem.
        :rtype: str
        """
        return f"Subsystem: {core_component.name}"
