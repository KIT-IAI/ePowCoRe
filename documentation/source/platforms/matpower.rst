MATPOWER
========

From MATPOWER's `about page <https://matpower.org/about/>`_:

    MATPOWER is a package of free, open-source Matlab-language M-files for solving steady-state power system simulation and optimization problems, such as:

    * power flow (PF),
    * continuation power flow (CPF),
    * extensible optimal power flow (OPF),
    * unit commitment (UC) and
    * stochastic, secure multi-interval OPF/UC.

MATPOWER is also the underlying engine behind :doc:`JMDL (eASiMOV) </platforms/jmdl>`.


GDF → MATPOWER
--------------

* p.u. values need to be based on global base rating, not individual component rating -- as is the case in GDF.