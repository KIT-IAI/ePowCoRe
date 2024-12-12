import json
import os
import pathlib
import time

from epowcore.gdf.core_model import CoreModel
from epowcore.pandapower.pandapower_converter import PandapowerConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "IEEE39"

    start = time.perf_counter()

    with open(PATH.parent / f"output/gdf/{model_name}_gdf.json", "r", encoding="utf-8") as file:
        data_str = file.read()
        data = json.loads(data_str)
        core_model = CoreModel.import_dict(data)

        converter = PandapowerConverter(debug=False)
        pandapower_model = converter.from_gdf(
            core_model, f"{model_name}", log_path=str(PATH.parent / "pandapower.log")
        )

        # Create directory if it does not exist
        if not os.path.exists("output/pandapower"):
            os.makedirs("output/pandapower")
        converter.write_to_pandapower_json(
            model=pandapower_model, filepath=f"output/pandapower/{model_name}.json"
        )

        print(f"conversion took {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
