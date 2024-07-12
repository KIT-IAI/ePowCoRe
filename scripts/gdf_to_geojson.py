import json
import os
import pathlib
import time

import geojson

from epowcore.gdf.data_structure import DataStructure
from epowcore.geo_json.geo_json_converter import GeoJSONConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "IEEE39"

    start = time.perf_counter()

    with open(
        PATH.parent / f"output/gdf/{model_name}_gdf.json", "r", encoding="utf-8"
    ) as file:
        data_str = file.read()
    data = json.loads(data_str)
    data_struct = DataStructure.import_dict(data)

    converter = GeoJSONConverter(debug=False)
    geo_json_model = converter.from_gdf(
        data_struct, f"{model_name}", log_path=str(PATH.parent / "geojson.log")
    )

    # Create directory if it does not exist
    if not os.path.exists("output/geojson"):
        os.makedirs("output/geojson")
    with open(f"output/geojson/{model_name}.geojson", "w", encoding="utf8") as file:
        file.write(geojson.dumps(geo_json_model, indent=2))

    print(f"conversion took {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
