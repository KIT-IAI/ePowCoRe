from epowcore.gdf.core_model import CoreModel
from epowcore.power_factory.power_factory_model import PowerFactoryModel


class PowerFactoryExporter:
    """Class holding the powerfactory application instance doing all the converting to then
    retur a PowerfactoryModel in the main export export function.
    """
    
    
    
    def export_power_factory(core_model: CoreModel, name: str) -> PowerFactoryModel:
        