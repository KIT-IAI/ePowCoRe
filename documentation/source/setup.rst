Setup
=====

Most of the integrations require the relevant software to be installed and licensed on the system.
As some of the software is only available for Windows, instructions are tested on the current version of Windows 11.
The tested versions of the software are listed below.

+----------+--------------------+
| Software | Version            |
+==========+====================+
| Windows  | 11 Pro 23H2        |
+----------+--------------------+
| Python   | 3.10.X 64-bit      |
+----------+--------------------+
| Matlab   | R2022b             |
+----------+--------------------+
| Simscape | 5.5/Electrical 7.9 |
+----------+--------------------+
| Simulink | 10.7               |
+----------+--------------------+
| RSCAD FX | 1.2                |
+----------+--------------------+
| PF       | 2022 SP2           |
+----------+--------------------+

Installation
------------
To install this project, perform the following steps:

1. Clone the project
2. :code:`cd` into the cloned directory
3. Install Python 3.10.11 64-bit
4. Create a virtual environment with :code:`<path to python 3.10.11>/python -m venv <path to virtual environment>`
5. Activate the virtual environment with :code:`<path to virtual environment>\\Scripts\\activate.bat` or :code:`<path to virtual environment>\\Scripts\\activate.ps1`
6. :code:`pip install .[dev]` or :code:`pip install -e .[dev]` to install the project editable.

VS Code Recommended Extensions
------------------------------
The following extensions are recommended for VS Code:

1. Python (Microsoft)
2. Black Formatter (Microsoft)
3. Extension Pack for Restructured Text (lextudio)
4. Mypy (Matan Gover)
5. Pylint (Microsoft)

Matlab
------
Install the current Matlab version and the Simulink, Simscape and Simscape Electrical add-ons.
The integration is provided by a pip package, no further configuration should be required.

.. note:: 
  Matlabengine is the pip package that provides the integration with Matlab.
  Each version of matlabengine typically supports one specific version of MATLAB and requires one of the versions of Python current at release of the package.
  Please check compatibility at `PyPI <https://pypi.org/project/matlabengine/#history>`_ before upgrading.

  We pinned matlabengine to **9.13.9** to support Matlab R2022b and Python 3.11.4. 

RSCAD FX / pyapi_rts
--------------------
The integration is provided by the pyapi_rts package, RSCAD FX does not need to be installed.
pyapi_rts might need additional configuration before use, please consult the relevant documentation.
Please also check compatibility with your version of RSCAD FX.

PowerFactory
------------
PowerFactory requires the path to the module to be added to the python environment.
Different methods are available to do this, the following have been tested:

- In your Python environment, e.g. :code:`C:\\Users\\USERNAME\\.conda\\envs\\ENVNAME`
- In the directory :code:`Lib\\site-packages`
- Add a file called :code:`powerfactory.pth` with the location of the required PowerFactory Python library in a single line
  - e.g. :code:`C:\\Program Files\\DIgSILENT\\PowerFactory 2022\\Python\\3.10`

eASiMOV
-------
eASiMOV does not need to be installed for the integration to work.
Compatibility is tested with the version mentioned above, but other versions might work as well.
