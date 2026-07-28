PyPSA
=====

From the `PyPSA documentation <https://docs.pypsa.org/v1.2.4/>`_:
    PyPSA is an open-source Python framework for optimising and simulating modern power and energy systems that include features such as conventional generators with unit commitment, variable wind and solar generation, hydro-electricity, inter-temporal storage, coupling to other energy sectors, elastic demands, and linearised power flow with loss approximations in DC and AC networks. PyPSA is designed to scale well with large networks and long time series. It is made for researchers, planners and utilities with basic coding aptitude who need a fast, easy-to-use and transparent tool for power and energy system analysis.

GDF → pandapower
----------------

Currently, the bus voltage magnitude is deviating from the powerflow results of pandapower by more than 5%.

The conversion process is a relatively simple conversion which happens for all components per conversion type.
Some component types, which PyPSA cannot represent directly, are replaced by other components beforehand.

These are:

* Three Winding Transformer
* Wards
* Extended Wards
* Impedances
* Switches (these are not converted, but replaced with a transmission line if the switch is closed)

The complete conversion implementation state for all components can be found in the respective section.
