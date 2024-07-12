RSCAD FX
========

GDF → RSCAD FX
---------------
The import and export to the RTDS \*.dfx format is handled by the pyapi_rts module.
This works independent of RSCAD FX and can generate new \*.dfx files from scratch.

The two-winding transformer and the three-winding transformer use the port names to connect to the correct connection points and can be used as an example for other components.

During the pre-export, the model is flattened by replacing the subsystems with their contents as the exporter creates its own hierarchy.

The export requires creating hierarchies for each bus because connections in RSCAD FX are represented by having the components touch at their connection points on the canvas.
The exporter creates a hierarchy for each bus and the components it is directly connected to.
The bus hierarchies that are connected via another component are then placed in a higher hierarchy.
This is done recursively until only one bus remains, which is the root of the hierarchy.

In addition, the load costs of components are tracked and subsystems with a load cost that gets too high are split into multiple subsystems.

Connections
^^^^^^^^^^^
RSCAD FX allows connecting components by having two buses with the same name and connecting the components to those buses.
This is used in the ``RscadCanvasDrawer`` to create connections without having to draw wires on the canvas.
After all buses have their own hierarchy with the components directly connected to them, the subgraphs of connected nodes can be merged into higher hierarchies. (see ``RscadCanvasDrawer.bus_hierarchies_to_hierarchy``).
All bus components that are only connected are then placed at the same spot to connect them. The other bus components are placed at the connection points of the bus components they are connected to.

Supported Components
--------------------
* Bus
* DyLoad
* IEEEG1
* IEEEST1A
* IEEEST1A
* IEEEPSS1A
* PTIST1
* Synchronous Machine
* Three-Winding Transformer
* Two-Winding Transformer

RSCAD FX → GDF
---------------
Not implemented.