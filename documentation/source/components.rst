Components
==========

* |:heavy_check_mark:| **Supported**: The GDF component is converted directly to an equivalent of the target platform and vice versa.
* |:wavy_dash:| **Converted**: There is no direct equivalency between the GDF component and the target platform, but the component is converted to adequately represent the original.
* |:x:| **Not supported**: The component is ignored during the conversion process.

General Power System Components
-------------------------------

.. csv-table::
   :header: "GDF Component", "JMDL", "PF", "RSCAD", "Simscape", "pandapower", "pyPSA"
   :widths: 15, 10, 10, 10, 10, 10, 10

   "Bus",               "|:heavy_check_mark:|", "|:heavy_check_mark:|", "|:heavy_check_mark:|", "|:heavy_check_mark:|", "|:heavy_check_mark:|", "|:heavy_check_mark:|"
   "Extended Ward",     "|:wavy_dash:|",        "|:heavy_check_mark:|", "|:x:|",                "|:x:|",               "",                     "|:x:|"
   "External Grid",     "",                     "",                     "",                     "",                   "|:heavy_check_mark:|", "|:wavy_dash:|"
   "Impedance",         "",                     "",                     "",                     "",                   "",                     "|:wavy_dash:|"
   "Load",              "",                     "",                     "",                     "",                   "|:heavy_check_mark:|", "|:heavy_check_mark:|"
   "Shunt",             "",                     "",                     "",                     "",                   "|:heavy_check_mark:|", "|:heavy_check_mark:|"
   "Switch",            "",                     "",                     "",                     "",                   "|:heavy_check_mark:|", "|:x:|"
   "Subsystem",         "",                     "",                     "",                     "",                   "|:x:|",                "|:x:|"
   "Transmission line", "",                     "",                     "",                     "",                   "|:heavy_check_mark:|", "|:heavy_check_mark:|"
   "Voltage Source",    "",                     "",                     "",                     "",                   "",                     "|:wavy_dash:|"
   "Ward",              "",                     "",                     "",                     "",                   "|:heavy_check_mark:|", "|:wavy_dash:|"
   "PV System",         "",                     "",                     "",                     "|:heavy_check_mark:|", "|:heavy_check_mark:|", "|:heavy_check_mark:|"


Generation
----------

.. csv-table::
   :header: "GDF Component", "JMDL", "PF", "RSCAD", "Simscape", "pandapower", "PyPSA"
   :widths: 15, 8, 8, 8, 10, 10, 10

   "EPow Gen.",        "", "", "", "", "", "|:wavy_dash:|"
   "Generator",        "", "", "", "", "", ""
   "Sync. Mach.",      "", "", "", "", "|:heavy_check_mark:|", "|:heavy_check_mark:|"
   "Static Generator", "", "", "", "", "|:wavy_dash:|",        "|:wavy_dash:|"
   "PV System",        "", "", "", "|:heavy_check_mark:|", "|:heavy_check_mark:|", "|:wavy_dash:|"


Generator Control
-----------------

Exciters
^^^^^^^^

.. csv-table::
   :header: "GDF Component", "JMDL", "PF", "RSCAD", "Simscape", "pandapower", "PyPSA"
   :widths: 15, 8, 8, 8, 10, 10, 10

   "IEEEST1A", "", "", "", "", "", "|:x:|"
   "IEEET1",   "", "", "", "", "", "|:x:|"


Governors
^^^^^^^^^

.. csv-table::
   :header: "GDF Component", "JMDL", "PF", "RSCAD", "Simscape", "pandapower", "PyPSA"
   :widths: 15, 8, 8, 8, 10, 10, 10

   "IEEEG1", "", "", "", "", "", "|:x:|"

Power System Stabilizers
^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "GDF Component", "JMDL", "PF", "RSCAD", "Simscape", "pandapower", "PyPSA"
   :widths: 15, 8, 8, 8, 10, 10, 10

   "IEEEPSS1A", "", "", "", "", "", "|:x:|"
   "Stabilizer",  "", "", "", "", "", "|:x:|"
   "PTIST1",      "", "", "", "", "", "|:x:|"


Transformers
------------

.. csv-table::
   :header: "GDF Component", "JMDL", "PF", "RSCAD", "Simscape", "pandapower", "PyPSA"
   :widths: 15, 8, 8, 8, 10, 10, 10

   "EPow. Trans.", "", "", "", "", "",                     ""
   "3-winding",    "", "", "", "", "|:heavy_check_mark:|", "|:wavy_dash:|"
   "2-winding",    "", "", "", "", "|:heavy_check_mark:|", "|:heavy_check_mark:|"



