from geojson import Point, FeatureCollection, Feature, LineString, utils

from epowcore.gdf import DataStructure
from epowcore.generic.logger import Logger


def export_geo_json(data_structure: DataStructure) -> FeatureCollection:
    geo_json_objects = []

    for node in data_structure.graph.nodes:
        if node.coords is not None and node.coords:
            properties = {
                "uid": node.uid,
                "name": node.name,
                "type": node.__class__.__name__,
            }
            if isinstance(node.coords, tuple):
                geo_json_objects.append(
                    Feature(
                        id=node.uid,
                        geometry=Point((node.coords[1], node.coords[0])),
                        properties=properties,
                    )
                )
            else:
                line = utils.map_tuples(lambda c: (c[1], c[0]), LineString(node.coords))
                geo_json_objects.append(
                    Feature(
                        id=node.uid,
                        geometry=line,
                        properties=properties,
                    )
                )
        else:
            Logger.log_to_selected(f"No coordinates for {node.name} ({node.uid}). Not exported!")

    return FeatureCollection(geo_json_objects)
