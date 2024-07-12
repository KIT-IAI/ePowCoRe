Simscape (MATLAB/Simulink)
==========================

Simscape is a MATLAB toolbox for the simulation of electrical power systems.
It is based on the Simscape toolbox and uses the Simscape language to describe the system.
It can be installed via the MATLAB Add-Ons menu.

Software
--------

+---------------------+----------------------------------------------------------------------------+
| Name                | Description                                                                |
+=====================+============================================================================+
| MATLAB              | Programming/Scripting language with focus on mathematical equations        |
+---------------------+----------------------------------------------------------------------------+
| Simulink            | Graphical programming environment for MATLAB                               |
+---------------------+----------------------------------------------------------------------------+
| Simscape            | Extension of the MATLAB Engine to add new domains and components to MATLAB |
+---------------------+----------------------------------------------------------------------------+
| Simscape Electrical | Simscape add-on for electrical components                                  |
+---------------------+----------------------------------------------------------------------------+


GDF → Simscape
--------------
Creates a Simscape model from a GDF file.
The following components are currently supported:

* Bus
* Load
* TLine
* IEEEST1A
* IEEEPSS1A
* IEEEG1
* 2-winding-transformer
* 3-winding-transformer

Adding New Components
^^^^^^^^^^^^^^^^^^^^^

**Prerequesites:**

- GDF component is already implemented

**Steps:**

- Add the Simscape block path to the ``SimscapeBlockType`` enum in ``epowcore/simscape/shared.py``
- Add the port handle mapping to the ``PORT_HANDLES`` dictionary in ``epowcore/simscape/port_handles.py``
- Implement Simscape block creation and parameter setting
    - Add a module in ``epowcore/simscape/components`` for the new component
- Add the new creation function to ``__create_components()`` in ``export.py``
- If used in a subsystem template, add the parameter setter to ``insert_subsystem_template()`` in ``subsystem_helper.py``


Connections
-----------
Connections between components are represented by lines.
Lines are identified by their LineHandles and can be connected to multiple components.

The mapping from GDF port names to Simscape ports is done with the ``Simscape.PortHandles`` configuration dictionary.
It uses a Component class as key to map the GDF port names to the Simscape port handles consisting of name, start (index) and length.

The common port names in Simscape are ``Outport`` and ``Inport`` for data signals and ``LConn`` and ``RConn`` for electrical ports.

This mapping can be accessed via the ``ConfigManager.get_specific_porthandles(block_type, port_name)`` function.


Example::

    # Scenario: An edge connecting an IEEEST1A component is labeled with "Out".
    PortHandles[IEEEST1A] = {"In": {...}, "Out": {...}}
    PortHandles[IEEEST1A]["Out"] = {name: "Outport", start: 0, length: 1}

    # Access with ConfigManager
    ConfigManager.get_specific_porthandles(SimscapeBlockType.IEEEST1A, "Out") => PortHandles("Outport", 0,1)


Subsystems
----------

.. warning::

    Whole section is outdated!

Subsystems are used to group components together.
The ``subsystem.insert_subsystem`` function can create a subsystem from a *template*, meaning an existing model or subsystem in a model.

*Variant Subsystems* are also supported, allowing similar subsystems to be created from a single template.
The relevant variant is selected via the `variant label <https://de.mathworks.com/help/simulink/slref/variantsubsystemvariantmodelvariantassemblysubsystem.html>`_.

The ``extra_params`` dictionary can be used to further modify the subsystem.
The keys are relative to the subsystem, e.g. ``{'IEEEST1A.R' : 0.1}`` will set the ``R`` parameter of the ``IEEEST1A`` component in the subsystem.
The ``lower_subsystem_variant_labels`` parameter can be used to modify the variant labels of subsystems within the subsystem. This even works for Variant Subsystems multiple layers deep.


Simscape → GDF
--------------
Not implemented.

.. note:: 

    For testing of the exporter, methods to get the connections between Simscape components were evaluated.
    Using the ``SrcBlockHandle`` and ``DstBlockHandle`` methods proved to be unreliable as no result is provided when the connected line has more than two connections.
    Reading the ``LineHandles`` from a given component and checking the ``Points`` property of the lines for overlap proved to be more reliable, but is still not perfect.
