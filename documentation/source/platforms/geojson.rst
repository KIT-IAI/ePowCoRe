GeoJSON
=======

    GeoJSON is a format for encoding a variety of geographic data structures.
    https://geojson.org/

This platforms builds heavily on the ``geojson`` Python package: https://github.com/jazzband/geojson


GDF → GeoJSON
-------------

The GeoJSON export only consideres components on the top level of the ``CoreModel``.
It does not traverse into subsystems.
Furthermore, only components with available coordinates are exported.
The only distinguishing factor between exported components is the number of coordinates:

- One coordinate pair: exported as ``Point``
- Multiple coordinate pairs: exported as a ``LineString``
