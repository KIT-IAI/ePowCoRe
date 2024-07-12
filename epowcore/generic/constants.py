from enum import Enum


GDF_VERSION = 1


class Platform(Enum):
    GEOJSON = "GeoJSON"
    JMDL = "JMDL"
    MATPOWER = "Matpower"
    POWERFACTORY = "PowerFactory"
    RSCAD = "RSCAD"
    SIMSCAPE = "Simscape"
