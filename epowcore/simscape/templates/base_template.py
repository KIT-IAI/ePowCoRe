from abc import ABC, abstractmethod
from epowcore.gdf.component import Component

from epowcore.gdf.subsystem import Subsystem
from epowcore.simscape.port_handles import PortHandles


class SubsystemTemplate(ABC):
    """A base class for Simscape subsystem templates."""

    template_file_name: str
    port_handles: list[PortHandles]

    @classmethod
    @abstractmethod
    def check_match(cls, subsystem: Subsystem) -> bool:
        """Check if the template matches the given subsystem.

        :param subsystem: The subsystem under test.
        :type subsystem: Subsystem
        :return: Whether or not the template can be applied here.
        :rtype: bool
        """

    @classmethod
    @abstractmethod
    def get_variant_labels(cls, subsystem: Subsystem) -> dict[str, str]:
        """Get the variant labels for the given subsystem.

        :param subsystem: The subsystem to get the labels for.
        :type subsystem: Subsystem
        :return: A dictionary with label names and values.
        :rtype: dict[str, str]
        """

    @classmethod
    @abstractmethod
    def get_component_mapping(cls, subsystem: Subsystem) -> dict[Component, str]:
        """Map the relevant component in the subsystem to the corresponding Simscape blocks.

        :param subsystem: The subsystem to create the mapping for.
        :type subsystem: Subsystem
        :return: The mapping from generic components to Simscape blocks in the subsystem.
        :rtype: dict[Component, str]
        """
