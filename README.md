# Generic Model Converter

## Installation

Please look at the documentation 'Setup' page for setup instructions.

## Usage

- A script to convert from PowerFactory to JMDL is available at `scripts/pf_to_jmdl.py`.
- As of now, you have to edit the script to change the desired PowerFactory project and output file.
- Run the script: `python .\scripts\pf_to_jmdl.py`
- Other scripts to convert to different formats are available as well.

## Documentation

The source for the documention is available in the `documentation\source` directory.
While it is possible to read the source on its own, an HTML version of the documentation offers a nicer formatting and search capabilities.

You can download an HTML version [here](https://gitlab.kit.edu/api/v4/projects/156718/jobs/artifacts/main/download?job=pages).
Unzip the `download` file, and open `documentation\build\html\index.html` to start.

Alternatively, you can build the HTML documentation yourself by following the command line instructions of the `pages.script` part in the GitLab CI configuration file: `.gitlab-ci.yml`

## Project Structure: epowcore

- `gdf` (Generic Data Format): Contains the overall generic data structure, component models, and other basic classes.
- `jmdl`, `power_factory`, `rscad`: Contain the platform specific methods for format conversions.

## Testing & Coverage

    pytest --cov=epowcore tests/; coverage xml
