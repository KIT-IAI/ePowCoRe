import json
import os
import pathlib
import pprint
import time

import numpy as np
import pandas as pd
from pypsa import network

from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.load import Load
from epowcore.pypsa.pypsa_convert import PyPSAConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "GredlerAreal4_1"

    pd.set_option("future.no_silent_downcasting", True)

    start = time.perf_counter()

    with open(
        PATH.parent / f"tests/models/gdf/IEEE39-flat_gdf.json", "r", encoding="utf-8"
    ) as file:
        data_str = file.read()
        data = json.loads(data_str)
        core_model = CoreModel.import_dict(data)

        converter = PyPSAConverter(debug=False)
        pypsa_model: network = converter.from_gdf(
            core_model, f"{model_name}", log_path=str(PATH.parent / "pypsa.log")
        )

        # Create directory if it does not exist
        # if not os.path.exists("output/pandapower"):
        #     os.makedirs("output/pandapower")
        # converter.write_to_pandapower_json(
        #     model=pandapower_model, filepath=f"output/pandapower/{model_name}.json"
        # )

        print(f"conversion took {time.perf_counter() - start:.1f}s")

        pypsa_model.consistency_check()
        # pypsa_model.lpf()
        # pypsa_model.optimize()
        # pypsa_model.fix_optimal_dispatch()

        result = pypsa_model.pf()
        print(result)


if __name__ == "__main__":
    main()
