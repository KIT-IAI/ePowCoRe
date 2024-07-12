from abc import abstractmethod
import random
import string
from typing import Generic, TypeVar

from epowcore.gdf.core_model import CoreModel
from epowcore.generic.converter_base import ConverterBase

Model = TypeVar("Model")
"""An identifier for a model in the format being tested."""


class FormatTestBase(Generic[Model]):
    def __init__(self, converter: ConverterBase, core_model: CoreModel) -> None:
        """
        Initializes the converter and uses it to export the core model to the format.
        """
        self.converter = converter
        name = "".join(random.choices(string.ascii_letters, k=10))
        self.model = converter.from_gdf(core_model, name)

    @abstractmethod
    def component_count(self) -> int:
        """Count the number of components in the model."""

    @abstractmethod
    def contains_subsystem(self) -> bool:
        """Check if the model contains subsystems."""

    @abstractmethod
    def delete(self) -> bool:
        """Delete the model."""
