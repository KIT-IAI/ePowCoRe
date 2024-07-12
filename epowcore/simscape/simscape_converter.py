import matlab.engine

from epowcore.gdf.data_structure import DataStructure
from epowcore.generic.converter_base import ConverterBase
from epowcore.generic.manipulation.group_subsystem_rules import (
    apply_group_subsystem_rules,
)
from epowcore.simscape.export import export
from epowcore.simscape.simscape_graph_transformer import rename_duplicate_nodes


class SimscapeConverter(ConverterBase[str]):
    """Converter for Matlab/Simscape models."""

    def __init__(self, eng: matlab.engine.MatlabEngine | None = None, debug: bool = False) -> None:
        """
        :param eng: Matlab engine to use. If None, a new engine will be started.
        :param debug: If True, debug information and plots will be generated.
        """
        if eng is None:
            eng = matlab.engine.start_matlab()  # type: ignore
            if not isinstance(eng, matlab.engine.MatlabEngine):
                raise TypeError("Matlab engine not started")
        self.eng: matlab.engine.MatlabEngine = eng
        self._apply_rules = True
        self._is_subsystem = False

        super().__init__(debug)

    def from_gdf(
        self,
        ds: DataStructure,
        name: str,
        log_path: str | None = None,
        *,
        apply_rules: bool = True,
        is_subsystem: bool = False,
    ) -> str:
        self._apply_rules = apply_rules
        self._is_subsystem = is_subsystem
        return super().from_gdf(ds, name, log_path)

    def _pre_export(self, ds: DataStructure, name: str) -> DataStructure:
        ds.graph = rename_duplicate_nodes(ds.graph)
        if self._apply_rules:
            apply_group_subsystem_rules(ds)
        return ds

    def _export(self, ds: DataStructure, name: str) -> str:
        export(ds, name, self.eng, is_subsystem=self._is_subsystem)
        return name

    def _import(self, model: str) -> DataStructure:
        raise NotImplementedError()
