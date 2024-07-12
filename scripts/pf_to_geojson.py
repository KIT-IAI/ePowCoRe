import os
import pathlib

import geojson

from epowcore.geo_json.geo_json_converter import GeoJSONConverter
from epowcore.power_factory.power_factory_converter import PFModel, PowerFactoryConverter

PATH = pathlib.Path(__file__).parent.resolve()


def main() -> None:
    model_name = "IEEE39"
    study_case_name = None
    frequency = 50.0
    log_path = str(PATH.parent / f"pf_geojson_{model_name}.log")

    pf_converter = PowerFactoryConverter()
    data_structure = pf_converter.to_gdf(
        PFModel(model_name, study_case_name, frequency), log_path=log_path
    )

    geo_converter = GeoJSONConverter()
    geo_json_model = geo_converter.from_gdf(data_structure, model_name, log_path=log_path)

    # Create directory if it does not exist
    if not os.path.exists("output/geojson"):
        os.makedirs("output/geojson")
    with open(f"output/geojson/{model_name}.geojson", "w", encoding="utf8") as file:
        file.write(geojson.dumps(geo_json_model, indent=2))


if __name__ == "__main__":
    main()
