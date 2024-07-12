import json
import os
import pathlib
import time

from epowcore.gdf.data_structure import DataStructure
from epowcore.matpower.matpower_converter import MatpowerConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "IEEE39"

    start = time.perf_counter()

    with open(PATH.parent / f"output/gdf/{model_name}_gdf.json", "r", encoding="utf-8") as file:
        data_str = file.read()
    data = json.loads(data_str)
    data_struct = DataStructure.import_dict(data)

    converter = MatpowerConverter(debug=False)
    matpower_model = converter.from_gdf(
        data_struct, f"{model_name}", log_path=str(PATH.parent / "matpower.log")
    )

    # Create directory if it does not exist
    if not os.path.exists("output/matpower"):
        os.makedirs("output/matpower")
    converter.write_to_matfile(matpower_model, f"output/matpower/{model_name}.mat")

    print(f"conversion took {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
