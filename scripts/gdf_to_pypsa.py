import json
import os
import pathlib
import time

import pandas as pd
from pypsa import network

from epowcore.gdf.core_model import CoreModel
from epowcore.pypsa.pypsa_convert import PyPSAConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "IEEE39_gdf"

    pd.set_option("future.no_silent_downcasting", True)

    start = time.perf_counter()

    with open(PATH.parent / f"tests/models/gdf/{model_name}.json", "r", encoding="utf-8") as file:
        data_str = file.read()
        data = json.loads(data_str)
        core_model = CoreModel.import_dict(data)

        converter = PyPSAConverter(debug=False)
        pypsa_model: network = converter.from_gdf(
            core_model, f"{model_name}", log_path=str(PATH.parent / "pypsa.log")
        )

        if not os.path.exists("output/pypsa"):
            os.makedirs("output/pypsa")
        pypsa_model.export_to_netcdf(path=f"output/pypsa/{model_name}.nc")

        print(f"conversion took {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
