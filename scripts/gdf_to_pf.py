import json
import os
import pathlib
import time

from epowcore.generic.tools.visualization import visualize_graph
from epowcore.generic.component_graph import ComponentGraph
from epowcore.gdf.core_model import CoreModel
from epowcore.power_factory.power_factory_converter import PowerFactoryConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "roegling_no_sites_v2"

    start = time.perf_counter()

    # Create directory if it does not exist
    if not os.path.exists("output/power_factory"):
        os.makedirs("output/power_factory")

    with open(
        PATH.parent / f"output/gdf/{model_name}_gdf.json", "r", encoding="utf-8"
    ) as file:
        data_str = file.read()
        data = json.loads(data_str)
        core_model = CoreModel.import_dict(data)

        cg = ComponentGraph(graph=core_model.graph)
        print("sanity: " + str(cg.sanity_check()))

        converter = PowerFactoryConverter(debug=False)
        power_factory_model = converter.from_gdf(
            core_model,
            f"{model_name}_second_conversion",
            log_path=str(PATH.parent / "power_factory.log"),
        )
        print(power_factory_model)

    print(f"conversion took {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
