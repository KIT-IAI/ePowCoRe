import json
import os
import pathlib

from epowcore.gdf.core_model import CoreModel
from epowcore.generic.manipulation.remove_internal_nodes import remove_internal_nodes

from epowcore.jmdl.jmdl_converter import JmdlConverter


PATH = pathlib.Path(__file__).parent.resolve()


def main():
    model_name = "IEEE39"

    with open(PATH.parent / f"output/gdf/{model_name}_gdf.json", "r", encoding="utf-8") as file:
        data_str = file.read()
    data = json.loads(data_str)
    core_model = CoreModel.import_dict(data)

    reduced_core_model = remove_internal_nodes(core_model)

    converter = JmdlConverter()
    jmdl = converter.from_gdf(reduced_core_model, model_name, log_path=str(PATH.parent / "jmdl.log"))
    if not os.path.exists("output/jmdl"):
        os.makedirs("output/jmdl")
    with open(f"output/jmdl/{model_name}.jmdl", "w", encoding="utf-8") as file:
        file.write(jmdl.to_json())


if __name__ == "__main__":
    # cProfile.run('main()')
    main()
