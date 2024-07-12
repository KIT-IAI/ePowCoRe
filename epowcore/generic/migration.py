import copy
from epowcore.generic.constants import GDF_VERSION


def migrate_json(data: dict) -> tuple[dict, list[str]]:
    data = copy.deepcopy(data)
    version = data.get("version", 0)
    changelog: list[str] = []
    if version == GDF_VERSION:
        return data, []
    if version < 1:
        changelog += _migrate_to_1(data)
    return data, changelog

def _migrate_to_1(data: dict) -> list[str]:
    changelog = ["## v1"]
    data["version"] = 1
    changelog.append("- Added version number 1.")
    return changelog
