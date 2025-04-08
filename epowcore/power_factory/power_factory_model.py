from dataclasses import dataclass

@dataclass
class PFModel:
    """A basic description for a PowerFactory project."""

    project_name: str
    study_case_name: str | None
    frequency: float