from abc import abstractmethod
import copy
from typing import Generic, TypeVar

from epowcore.gdf.data_structure import DataStructure
from epowcore.generic.logger import Logger
from epowcore.generic.tools.visualization import visualize_graph

Model = TypeVar("Model")
"""The type of the model in the format being converted to or from or an identifier for it."""


class ConverterBase(Generic[Model]):
    """Base class for all converters with import to and export from the GDF."""

    def __init__(self, debug: bool = False) -> None:
        self.debug = debug

    def from_gdf(
        self, ds: DataStructure, name: str, log_path: str | None = None
    ) -> Model:
        """Export a data structure to the format."""
        logger = None
        if log_path is not None or self.debug:
            logger = Logger.new(f"{type(self).__name__} Export", True)
        else:
            Logger.disable()

        ds = copy.deepcopy(ds)
        if self.debug:
            print("Before export:")
            visualize_graph(ds.graph.get_internal_graph(copy=False), show_labels=True)
        ds = self._pre_export(ds, name)
        if self.debug:
            print("After pre export:")
            visualize_graph(ds.graph.get_internal_graph(copy=False), show_labels=True)
        model: Model = self._export(ds, name)
        model = self._post_export(model, name)
        if log_path is not None and logger is not None:
            logger.save_to_file(log_path)
            logger.close()
        return model

    def to_gdf(self, model: Model, log_path: str | None = None) -> DataStructure:
        """Import a data structure from the format."""
        logger = None
        if log_path is not None:
            logger = Logger.new(f"{type(self).__name__} Import", True)
        else:
            Logger.disable()
        model = self._pre_import(model)
        ds: DataStructure = self._import(model)
        if self.debug:
            print("After import:")
            visualize_graph(ds.graph.get_internal_graph(copy=False), show_labels=True)
        self._post_import(ds)
        if self.debug:
            print("After post impport:")
            visualize_graph(ds.graph.get_internal_graph(copy=False), show_labels=True)
        if log_path is not None and logger is not None:
            logger.save_to_file(log_path)
            logger.close()
        return ds

    def _pre_export(self, ds: DataStructure, name: str) -> DataStructure:
        """Called before the export of a data structure."""
        return ds

    @abstractmethod
    def _export(self, ds: DataStructure, name: str) -> Model:
        """Called during the export of a data structure."""

    def _post_export(self, model: Model, name: str) -> Model:
        """Called after the export of a data structure."""
        return model

    def _pre_import(self, model: Model) -> Model:
        """Called before the import of a model."""
        return model

    @abstractmethod
    def _import(self, model: Model) -> DataStructure:
        """Called during the import of a model."""

    def _post_import(self, data_structure: DataStructure) -> None:
        """Called after the import of a model."""
