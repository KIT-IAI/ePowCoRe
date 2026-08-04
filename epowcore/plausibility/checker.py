from abc import ABC, abstractmethod
from dataclasses import asdict
import json
from pathlib import Path
from typing import Generic, TypeVar

from epowcore.plausibility.plausibility_result import PlausibilityResult


Model = TypeVar("Model")


class PlausibilityChecker(ABC, Generic[Model]):
    """Generic interface for post-export plausibility checks."""

    def run(
        self,
        model: Model,
        output_path: str | None = None,
        name: str = "model",
    ) -> PlausibilityResult:
        """Run checks and optionally write generated output."""
        result = self.check(model)

        if output_path is not None:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            self.save_result(
                result=result,
                filepath=output_dir / f"{name}_plausibility.json",
            )

            if result.isolated_areas:
                self.plot_isolated_areas(
                    model=model,
                    result=result,
                    filepath=output_dir / f"{name}_isolated_areas.png",
                )

        return result

    def save_result(
        self,
        result: PlausibilityResult,
        filepath: Path,
    ) -> None:
        """Write a plausibility result to JSON."""
        with filepath.open("w", encoding="utf-8") as file:
            json.dump(
                asdict(result),
                file,
                indent=2,
            )

    @abstractmethod
    def check(self, model: Model) -> PlausibilityResult:
        """Run format-specific plausibility checks."""

    @abstractmethod
    def plot_isolated_areas(
        self,
        model: Model,
        result: PlausibilityResult,
        filepath: Path,
    ) -> None:
        """Plot isolated network areas."""