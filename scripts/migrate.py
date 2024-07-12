import json
import pathlib

from epowcore.generic.migration import migrate_json

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "IEEE39"

    with open(
        PATH.parent / f"tests/models/gdf/{model_name}_gdf.json", "r", encoding="utf-8"
    ) as file:
        migrated_data_str = file.read()
    data = json.loads(migrated_data_str)
    migrated_data, changelog = migrate_json(data)
    migrated_data_str = json.dumps(migrated_data, indent=2)

    with open(
        PATH.parent / f"tests/models/gdf/{model_name}_v{migrated_data['version']}_gdf.json",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(migrated_data_str)

    with open(
        PATH.parent / f"tests/models/gdf/{model_name}_changelog_v{migrated_data['version']}.md",
        "w",
        encoding="utf-8",
    ) as file:
        file.write("\n".join(changelog))


if __name__ == "__main__":
    main()
