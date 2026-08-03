Supported Platforms
===================

.. toctree::
   :maxdepth: 1
   :glob:

   platforms/*


State of Implementation
-----------------------

This page provides an overview of the current state of the project and the missing features.

.. toctree::
   :maxdepth: 1
   :glob:

   components


Import/Export
^^^^^^^^^^^^^

Some test text

.. csv-table::
   :header: "Format", "From GDF", "To GDF"
   :widths: 20, 40, 40

   "JMDL",       "|:heavy_check_mark:|", "|:heavy_check_mark:|"
   "PowerFactory", "|:heavy_check_mark:|\ *", "|:heavy_check_mark:|"
   "RSCAD",      "|:heavy_check_mark:|", "|:x:|"
   "Simulink",   "|:heavy_check_mark:|", "|:x:|"
   "GeoJSON",    "|:heavy_check_mark:|", "|:x:|"
   "pandapower", "|:heavy_check_mark:|\ *", "|:x:|"
   "PyPSA",      "|:heavy_check_mark:|\ *", "|:x:|"

\* Tests for a maximum deviation of 5% on bus voltage magnitude, line active and reactive power and generator active and reactiver power are currently not passing.
Use the converted networks with caution.

Features
^^^^^^^^

.. csv-table::
   :header: "Format", "Subsystem", "Port Names"
   :widths: 20, 40, 40

   "JMDL",       "|:heavy_check_mark:|", "|:x:|"
   "PowerFactory", "\-",                  "|:heavy_check_mark:|"
   "RSCAD",      "|:x:|",                "|:heavy_check_mark:|"
   "Simulink",   "|:heavy_check_mark:|", "|:heavy_check_mark:|"
   "GeoJSON",    "N/A",                  "N/A"
   "pandapower", "N/A",                  "N/A"
   "PyPSA",      "N/A",                  "N/A"
