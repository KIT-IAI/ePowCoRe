<div align="center">

# ⚡ ePowCoRe

**A Generic Representation of Power Grids Enabling Open-Source Model Conversion Modules**

[![Tests](https://img.shields.io/github/actions/workflow/status/KIT-IAI/ePowCoRe/tests.yml?branch=main\&style=flat-square\&logo=github\&label=tests)](https://github.com/KIT-IAI/ePowCoRe/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square\&logo=python\&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/dependencies-uv-6E56CF?style=flat-square)](https://docs.astral.sh/uv/)
[![Documentation](https://img.shields.io/badge/docs-Read%20the%20Docs-8CA1AF?style=flat-square\&logo=readthedocs\&logoColor=white)](https://epowcore.readthedocs.io/)
[![License](https://img.shields.io/github/license/KIT-IAI/ePowCoRe?style=flat-square)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13827587.svg)](https://doi.org/10.5281/zenodo.13827587)

</div>

---

## Overview

**ePowCoRe** is a Python framework for converting electrical power-system models between different modeling and simulation environments.

At its core, ePowCoRe uses the **Generic Data Format (GDF)** as a platform-independent intermediate representation.

```text
Source Model
     │
     ▼
┌─────────────────────┐
│ Generic Data Format │
│        (GDF)        │
└─────────────────────┘
     │
     ▼
Target Model
```

Using GDF as the intermediate representation separates platform-specific import and export logic from the generic grid model.

This allows conversion modules to operate around a common representation instead of implementing direct converters between every pair of supported platforms.

---

## Installation

### Requirements

* **Python 3.11**
* **uv**

The project currently declares:

```text
Python >=3.11,<3.12
```

### Clone the repository

```bash
git clone https://github.com/KIT-IAI/ePowCoRe.git
cd ePowCoRe
```

### Install dependencies

Install the environment from the committed lock file:

```bash
uv sync --locked
```

Run Python inside the project environment with:

```bash
uv run python --version
```

### Optional integrations

Additional dependency groups are available for specific integrations.

For PyPSA:

```bash
uv sync --locked --group pypsa
```

For MATLAB / Simscape:

```bash
uv sync --locked --group simscape
```

---

## Usage

Conversion scripts are available in [`scripts/`](scripts/).

For example, to convert a PowerFactory model to GDF:

```bash
uv run python scripts/pf_to_gdf.py
```

To convert an existing GDF model to JMDL:

```bash
uv run python scripts/gdf_to_jmdl.py
```

Several conversion scripts currently contain model names, input paths, output paths, or other configuration directly in the script. Adjust the corresponding script for the model being converted before execution.

Generated models are typically written below:

```text
output/
```

---

## Supported Conversions

The repository currently provides scripts for the following conversion paths:

| Source       | Target       | Script                 |
| ------------ | ------------ | ---------------------- |
| PowerFactory | GDF          | `pf_to_gdf.py`         |
| GDF          | PowerFactory | `gdf_to_pf.py`         |
| JMDL         | GDF          | `jmdl_to_gdf.py`       |
| GDF          | JMDL         | `gdf_to_jmdl.py`       |
| GDF          | GeoJSON      | `gdf_to_geojson.py`    |
| PowerFactory | GeoJSON      | `pf_to_geojson.py`     |
| GDF          | MATPOWER     | `gdf_to_matpower.py`   |
| GDF          | pandapower   | `gdf_to_pandapower.py` |
| GDF          | PyPSA        | `gdf_to_pypsa.py`      |
| GDF          | RSCAD / RTDS | `gdf_to_rscad.py`      |
| GDF          | Simscape     | `gdf_to_simscape.py`   |

Support depends on the available component mappings for each platform and conversion direction.

See the [documentation](https://epowcore.readthedocs.io/) for platform-specific details.

---

## Project Structure

```text
ePowCoRe/
│
├── epowcore/
│   ├── gdf/
│   ├── generic/
│   ├── geo_json/
│   ├── jmdl/
│   ├── matpower/
│   ├── pandapower/
│   ├── power_factory/
│   ├── rscad/
│   └── simscape/
│
├── scripts/
├── tests/
├── tests_slow/
├── documentation/
├── config/
│
├── pyproject.toml
├── uv.lock
├── .pre-commit-config.yaml
├── STYLEGUIDE.md
└── README.md
```

### Package Overview

| Path                     | Purpose                                         |
| ------------------------ | ----------------------------------------------- |
| `epowcore/gdf`           | Generic Data Format and core power-system model |
| `epowcore/generic`       | Platform-independent model operations           |
| `epowcore/geo_json`      | GeoJSON conversion                              |
| `epowcore/jmdl`          | JMDL integration                                |
| `epowcore/matpower`      | MATPOWER integration                            |
| `epowcore/pandapower`    | pandapower integration                          |
| `epowcore/power_factory` | DIgSILENT PowerFactory integration              |
| `epowcore/rscad`         | RSCAD / RTDS integration                        |
| `epowcore/simscape`      | MATLAB Simscape integration                     |
| `scripts`                | Conversion and utility scripts                  |
| `tests`                  | Automated tests                                 |
| `tests_slow`             | Slower or environment-dependent tests           |
| `documentation`          | Sphinx documentation sources                    |

---

## Development

Project dependencies and tool configuration are defined in:

```text
pyproject.toml
```

Resolved dependency versions are stored in:

```text
uv.lock
```

After modifying dependencies:

```bash
uv lock
uv sync
```

Commit both `pyproject.toml` and `uv.lock` when dependency resolution changes.

---

## Testing

### Core test suite

The GitHub Actions workflow runs:

```bash
uv run pytest tests/core
```

Run the same suite locally before submitting changes:

```bash
uv run pytest tests/core
```

### Full test suite

To run the broader test suite:

```bash
uv run pytest tests/
```

Some integration tests require external software or platform-specific environments and may therefore not run on every development machine.

### Coverage

Run tests with coverage:

```bash
uv run pytest --cov=epowcore tests/
```

Generate the XML coverage report:

```bash
uv run coverage xml
```

---

## Code Quality

The repository uses **Black** and **isort**, configured through `pyproject.toml`.

Run all configured pre-commit hooks with:

```bash
uv run pre-commit run --all-files
```

Individual tools can also be run directly.

### Black

```bash
uv run black epowcore tests
```

### isort

```bash
uv run isort epowcore tests
```

Check for whitespace errors before committing:

```bash
git diff --check
```

Additional project conventions are documented in [`STYLEGUIDE.md`](STYLEGUIDE.md).

---

## Documentation

The documentation is hosted on Read the Docs:

**https://epowcore.readthedocs.io/**

Documentation sources are located in:

```text
documentation/source/
```

Build the HTML documentation locally with:

```bash
uv run sphinx-build \
  -b html \
  documentation/source \
  documentation/build/html \
  -c documentation/source/
```

The generated documentation is available in:

```text
documentation/build/html/
```

---

## Citation

### Software

If you use ePowCoRe in academic work, cite the archived software release:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13827587.svg)](https://doi.org/10.5281/zenodo.13827587)

### Publication

> M. Weber, A. Kocher, H. K. Çakmak, and V. Hagenmeyer,
> **“ePowCoRe: A Novel Generic Representation of Power Grids Enabling Open-Source Model Conversion Modules,”**
> *2024 Open Source Modelling and Simulation of Energy Systems (OSMSES)*,
> Vienna, Austria, 2024, pp. 1–6.
> doi: `10.1109/OSMSES62085.2024.10668981`

---

## License

ePowCoRe is distributed under the [MIT License](LICENSE).
