from dataclasses import asdict
import json
from pathlib import Path

import pandapower

from epowcore.gdf.core_model import CoreModel
from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import Platform
from epowcore.generic.converter_base import ConverterBase
from epowcore.generic.logger import Logger
from epowcore.pandapower.from_gdf.pandapower_export import export_pandapower
from epowcore.pandapower.pandapower_model import PandapowerModel
from epowcore.plausibility.pandapower_checker import (
    PandapowerPlausibilityChecker,
)
from epowcore.plausibility.result import PlausibilityResult


class PandapowerConverter(ConverterBase[PandapowerModel]):
    def __init__(
        self,
        debug: bool = False,
        run_plausibility_check: bool = False,
        plausibility_plot_path: str | None = None,
        plausibility_output_dir: str | None = None,
    ) -> None:
        super().__init__(debug=debug)
        self.run_plausibility_check = run_plausibility_check
        self.plausibility_plot_path = plausibility_plot_path
        self.plausibility_output_dir = plausibility_output_dir
        self.plausibility_result: PlausibilityResult | None = None

    def from_gdf(
        self,
        core_model: CoreModel,
        name: str,
        log_path: str | None = None,
    ) -> PandapowerModel:
        Configuration().default_platform = Platform.PANDAPOWER
        return super().from_gdf(core_model, name, log_path)

    def _export(
        self,
        core_model: CoreModel,
        name: str,
    ) -> PandapowerModel:
        return export_pandapower(core_model)

    def _post_export(
        self,
        model: PandapowerModel,
        name: str,
    ) -> PandapowerModel:
        if not self.run_plausibility_check:
            return model

        checker = PandapowerPlausibilityChecker()
        self.plausibility_result = checker.check(model.network)

        message = self.plausibility_result.summary()

        if not Logger.log_to_selected(message):
            print(message)

        if self.plausibility_output_dir is not None:
            output_dir = Path(self.plausibility_output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / f"{name}_plausibility.json"

            with output_file.open("w", encoding="utf-8") as file:
                json.dump(
                    asdict(self.plausibility_result),
                    file,
                    indent=2,
                )

            print(f"Plausibility results saved to: {output_file}")

        if (
            self.plausibility_plot_path is not None
            and self.plausibility_result.isolated_areas
        ):
            checker.plot_isolated_areas(
                model.network,
                self.plausibility_result,
                self.plausibility_plot_path,
            )

        return model

    def write_to_pandapower_json(
        self,
        model: PandapowerModel,
        filepath: str,
    ) -> None:
        pandapower.to_json(
            net=model.network,
            filename=filepath,
        )

    def _import(self, model):
        return model