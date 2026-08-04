from dataclasses import dataclass, field


@dataclass
class PlausibilityResult:
    converged: bool = False
    soft_voltage_violations: list[dict] = field(default_factory=list)
    hard_voltage_violations: list[dict] = field(default_factory=list)
    overloaded_lines: list[dict] = field(default_factory=list)
    overloaded_transformers: list[dict] = field(default_factory=list)
    isolated_areas: list[list[int]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def successful(self) -> bool:
        return (
            self.converged
            and not self.soft_voltage_violations
            and not self.hard_voltage_violations
            and not self.overloaded_lines
            and not self.overloaded_transformers
            and not self.isolated_areas
            and not self.errors
        )

    def summary(self) -> str:
        if self.successful:
            return "Plausibility check successful. No issues detected."

        messages = [
            f"Load flow converged: {self.converged}",
            f"Soft voltage violations: {len(self.soft_voltage_violations)}",
            f"Hard voltage violations: {len(self.hard_voltage_violations)}",
            f"Overloaded lines: {len(self.overloaded_lines)}",
            f"Overloaded transformers: {len(self.overloaded_transformers)}",
            f"Isolated areas: {len(self.isolated_areas)}",
            f"Errors: {len(self.errors)}",
        ]

        return "\n".join(messages)