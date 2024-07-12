from enum import Enum

from ..component import Component


class GeneratorCategory(Enum):
    """Enumeration of generator categories."""

    BATTERY = "Battery"
    BIOFUEL = "Biofuel"
    BIOGAS = "Biogas"
    COAL = "Coal"
    DIESEL = "Diesel"
    EXTERNAL_GRID = "External Grid"
    FUEL_CELL = "Fuel Cell"
    GAS = "Gas"
    GEOTHERMAL = "Geothermal"
    HVDC_TERMINAL = "HVDC Terminal"
    HYDRO = "Hydro"
    NUCLEAR = "Nuclear"
    OIL = "Oil"
    OTHER = "Other"
    PEAT = "Peat"
    PHOTOVOLTAIC = "Photovoltaic"
    PUMP_STORAGE = "Pump Storage"
    REACTIVE_COMPENSATION = "Reactive Compensation"
    RENEWABLE = "Renewable"
    SOLAR = "Solar"
    STORAGE = "Storage"
    THERMAL = "Thermal"
    TIDAL = "Tidal"
    WIND = "Wind"


class Generator(Component):
    """Base class for generators."""

    category: GeneratorCategory = GeneratorCategory.OTHER
