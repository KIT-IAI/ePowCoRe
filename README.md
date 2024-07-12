# ePowCoRe

*A Generic Representation of Power Grids Enabling Open-Source Model Conversion Modules*


## Installation

To install this project, perform the following steps:

1. Clone the project
2. Open a terminal of the virtual environment where you want to use the project
    - Tested with Python 3.10
3. `cd` into the cloned directory
4. `pip install .` or `pip install -e .` to install the project editable.
    - Use `pip install -e .[dev]` to install with development dependencies


## Usage

- Script that convert from PowerFactory to the generic format and from there to other formats are available in the `scripts` folder.
- As of now, you have to edit the specific script to change the desired model and output file.
- Run the script, e.g.: `python .\scripts\pf_to_jmdl.py`


## Documentation

The source for the documention is available in the `documentation\source` directory.
While it is possible to read the source on its own, an HTML version of the documentation offers a nicer formatting and search capabilities.

**Build the documentation:**

    sphinx-apidoc -f -d 3 -E -o ./documentation/source/apidoc ./epowcore/ ./epowcore/generic ./epowcore/jmdl ./epowcore/power_factory/ ./epowcore/rscad/ ./epowcore/simscape/ ./epowcore/geojson/
    sphinx-build -b html documentation/source documentation/build/html -c ./documentation/source/


## Project Structure: epowcore

- `gdf` (Generic Data Format): Contains the overall generic core model, component models, and other basic classes.
- `generic`: Contains generic data structures and methods that work on generic models.
- `geo_json`, `jmdl`, `matpower`, `power_factory`, `rscad`, `simscape`: Contain the platform specific methods for format conversions.


## Testing & Coverage

    pytest --cov=epowcore tests/; coverage xml
