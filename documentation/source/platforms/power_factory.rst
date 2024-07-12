PowerFactory
============

PF → GDF
---------

The PowerFactoryExtractor generates a CoreModel object from a PF study case.
First, the supported blocks are extracted, then all nodes are iterated over to extract the connections between the blocks. 


Supported Blocks
----------------

* Bus (ElmTerm)
* Load (ElmLod)
* 2-Winding Transformer (ElmTr2)
* 3-Winding Transformer (ElmTr3)
* Line (ElmLne)
* Synchronous Machine (ElmSym)
    * Exciters
        * avr_ESST1A
        * exc_IEEE_ST1A
    * PSS
        * pss_CONV
        * pss_IEEE_PSS1A
    * Governors
        * gov_IEEEG1
        * gov_IEEE_IEEEG1
* Ward Equivalent (ElmVac)
* Impedance (ElmZpu)
* External Grids (ElmXnet)
* Switches (ElmCoup)


Implementation
--------------

The PowerFactoryExtractor is implemented as a class that inherits from the BaseExtractor class. It uses the project name and study case name as a tuple to identify the model.

The importer is implemented in the PowerFactoryExtractor class and mostly maps components directly.