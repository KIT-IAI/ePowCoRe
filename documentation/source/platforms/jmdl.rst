JMDL (eASiMOV)
==============
The JMDL format is implemented in the ``JmdlModel`` directly, so no installation of eASiMOV or other additional software is required.
However, this also means support for the format is limited to the features of the converter and the converter needs to be updated manually to support other versions of the format.

JMDL format
^^^^^^^^^^^
eASiMOV saves models in the *zipped JSON Model (\*.zjm)* format, which is a zip file containing a JSON file with the *model data (\*.jmdl)* and additional data if required.

Generic Model Converter can read and write the JMDL format, so zjm files need to be unzipped first.
GDF parses the JMDL format from json into python objects and therefore only supports one version of the file format (*0.6*). The model can be found in ``epowcore/jmdl/jmdl_model.py``. 
Most missing values are replaced with default values that can be changed in the configuration file (:doc:`/configuration`).

Default values are also set during export, so the priority system for the configuration file can be used to create export profiles for different scenarios.

.. note:: 
   eASiMOV will throw a vague error mentioning a failure to parse SuperBlock '/' if connections to ports not found in the block are present. If this happens during development, check the connections generated during export for errors.


Super Blocks and Subsystems
^^^^^^^^^^^^^^^^^^^^^^^^^^^
eASiMOV uses Super Blocks as a way to group components into their own subsystems, which are connected to their parent system via ports.
This maps pretty well to GDF with its Subsystem and port system, so the converter will try to map Super Blocks to Subsystems and ports to ports.

Super Blocks support three different types of ports:

* In Port 
* Out Port
* Conserving Port

The exporter uses conserving ports for its ports as they, like GDF ports, are bidirectional.
The ports appear as blocks in the SuperBlocks and are addressed inside the SuperBlock as ``.{port_name}`` and as regular ports outside the SuperBlock as ``{SuperBlockName}.{port_name}``.

Nested subsystems are correctly converted to nested super blocks during export and vice versa.

Supported Blocks
----------------
The converter supports the following blocks:

* Bus
* External Grid
* Generator / PvSystem
* Line
* Load
* Shunt
* Switch
* Transformer
* Voltage Source


GDF → JMDL
-----------
JMDL requires a bus to be placed in between two non-bus components and does not allow two buses to be connected directly.
To convert a GDF model to JMDL, the converter will therefore merge neighboring buses and add a bus between each pair of connected components where none exists.
In addition, multiple connections between two components must be transformed into connections via multiple buses.
Additionally, buses without type and component types that don't exist, like 3-winding-transformers and ExtendedWards, are replaced by equivalent combinations of other components.

JMDL → GDF
-----------
The JMDL converter can import models from JMDL files and supports most component types and Super Blocks/Subsystems.
The connections do not contain port names, but could probably be mapped as the JMDL format provides its own port names.
