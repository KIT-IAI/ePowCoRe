import json
import os
import pathlib
import time

from epowcore.power_factory.power_factory_converter import PFModel, PowerFactoryConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main():
    model_name = "IEEE39"

    start = time.perf_counter()

    model = PFModel("39 Bus New England System", "4. EMT Simulation Fault Bus 03", 60)

    converter = PowerFactoryConverter()
    data_structure = converter.to_gdf(model, log_path=str(PATH.parent / f"pf_{model_name}.log"))

    data = data_structure.export_dict()
    data_str = json.dumps(data, indent=2)
    # WRITE MODEL TO JSON FILE
    if not os.path.exists("output/gdf"):
        os.makedirs("output/gdf")
    with open(PATH.parent / f"output/gdf/{model_name}_gdf.json", "w", encoding="utf-8") as file:
        file.write(data_str)

    print(f"conversion took {time.perf_counter() - start:.1f}s")

    ## IMPORT JSON FILE TO CHECK MODEL CONSISTENCY
    # with open(f"tests/out/{model_name}_gdf.json", "r", encoding="utf-8") as file:
    #     data_str = file.read()
    # data = json.loads(data_str)
    # data_struct = DataStructure.import_dict(data)

    # print(data_str)
    # visualize_graph(data_struct.graph)


if __name__ == "__main__":
    main()
