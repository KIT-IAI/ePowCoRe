import json
import pathlib

from epowcore.jmdl.jmdl_converter import JmdlConverter
from epowcore.jmdl.jmdl_model import JmdlModel

PATH = pathlib.Path(__file__).parent.resolve()


def main():
    model_name = "IEEE39"
    json_data = None
    with open(f"tests/models/jmdl/{model_name}.jmdl", "r", encoding="utf8") as file:
        json_data = json.loads(file.read())
    converter = JmdlConverter()
    data_structure = converter.to_gdf(JmdlModel.from_dict(json_data))

    data = data_structure.export_dict()
    data_str = json.dumps(data, indent=2)
    # WRITE MODEL TO JSON FILE
    with open(
        PATH.parent / f"output/gdf/{model_name}_gdf.json", "w", encoding="utf-8"
    ) as file:
        file.write(data_str)


if __name__ == "__main__":
    main()
