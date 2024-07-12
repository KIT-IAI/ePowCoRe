import json
import pathlib
import time

from epowcore.gdf.data_structure import DataStructure
from epowcore.simscape.simscape_converter import SimscapeConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "IEEE39"

    start = time.perf_counter()

    with open(PATH.parent / f"output/gdf/{model_name}_gdf.json", "r", encoding="utf-8") as file:
        data_str = file.read()
    data = json.loads(data_str)
    data_struct = DataStructure.import_dict(data)
    # take the data_struct object and create a simscape model from it
    converter = SimscapeConverter(debug=False)
    converter.from_gdf(
        data_struct,
        f"{model_name}",
        log_path=str(PATH.parent / f"simscape_{model_name}.log"),
    )

    print(f"conversion took {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
