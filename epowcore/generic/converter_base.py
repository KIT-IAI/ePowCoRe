from abc import abstractmethod
import copy
from typing import Generic, TypeVar

from epowcore.gdf.core_model import CoreModel
from epowcore.generic.logger import Logger
from epowcore.generic.tools.visualization import visualize_graph

Model = TypeVar("Model")
"""The type of the model in the format being converted to or from or an identifier for it."""


class ConverterBase(Generic[Model]):
    """Base class for all converters with import to and export from the GDF."""

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug

    def from_gdf(
        self, core_model: CoreModel, name: str, log_path: str | None = None
    ) -> Model:
        """Export a core model to the format."""
        logger = None
        if log_path is not None or self.debug:
            logger = Logger.new(f"{type(self).__name__} Export", True)
        else:
            Logger.disable()

        core_model = copy.deepcopy(core_model)
        if self.debug:
            print("Before export:")
            visualize_graph(core_model.graph.get_internal_graph(copy=False), show_labels=True)
        core_model = self._pre_export(core_model, name)
        if self.debug:
            print("After pre export:")
            visualize_graph(core_model.graph.get_internal_graph(copy=False), show_labels=True)
        model: Model = self._export(core_model, name)
        model = self._post_export(model, name)
        if log_path is not None and logger is not None:
            logger.save_to_file(log_path)
            logger.close()
        return model

    def to_gdf(self, model: Model, log_path: str | None = None) -> CoreModel:
        """Import a core model from the format."""
        logger = None
        if log_path is not None:
            logger = Logger.new(f"{type(self).__name__} Import", True)
        else:
            Logger.disable()
        model = self._pre_import(model)
        core_model: CoreModel = self._import(model)
        if self.debug:
            print("After import:")
            visualize_graph(core_model.graph.get_internal_graph(copy=False), show_labels=True)
        self._post_import(core_model)
        if self.debug:
            print("After post impport:")
            visualize_graph(core_model.graph.get_internal_graph(copy=False), show_labels=True)
        if log_path is not None and logger is not None:
            logger.save_to_file(log_path)
            logger.close()
        return core_model

    def _pre_export(self, core_model: CoreModel, name: str) -> CoreModel:
        """Called before the export of a core model."""
        return core_model

    @abstractmethod
    def _export(self, core_model: CoreModel, name: str) -> Model:
        """Called during the export of a core model."""

    def _post_export(self, model: Model, name: str) -> Model:
        """Called after the export of a core model."""
        return model

    def _pre_import(self, model: Model) -> Model:
        """Called before the import of a model."""
        return model

    @abstractmethod
    def _import(self, model: Model) -> CoreModel:
        """Called during the import of a model."""

    def _post_import(self, core_model: CoreModel) -> None:
        """Called after the import of a model."""
