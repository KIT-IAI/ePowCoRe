import json
import os
import pathlib
import time
from epowcore.gdf.core_model import CoreModel
from epowcore.rscad.rscad_converter import RscadConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "IEEE39"

    start = time.perf_counter()
    with open(PATH.parent / f"output/gdf/{model_name}_gdf.json", "r", encoding="utf-8") as file:
        data_str = file.read()
    data = json.loads(data_str)
    core_model = CoreModel.import_dict(data)
    converter = RscadConverter()
    rscad_model = converter.from_gdf(core_model, model_name)
    if not os.path.exists("output/rscad"):
        os.makedirs("output/rscad")
    rscad_model.write_file("output/rscad", f"{model_name}.dfx")
    print(f"conversion took {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
