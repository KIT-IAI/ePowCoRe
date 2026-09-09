<div align="center">

# ⚡ ePowCoRe

### *A Generic Representation of Power Grids Enabling Open-Source Model Conversion Modules*

<p>
  <img src="https://img.shields.io/github/actions/workflow/status/KIT-IAI/ePowCoRe/tests.yml?branch=main&style=for-the-badge&logo=github&label=Tests" alt="Tests">
  <img src="https://img.shields.io/badge/Python-Project-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/uv-Dependency%20Management-DE5FE9?style=for-the-badge" alt="uv">
  <img src="https://img.shields.io/badge/pandapower-3.x-1E90FF?style=for-the-badge" alt="pandapower">
  <img src="https://img.shields.io/badge/PowerFactory-Integration-F59E0B?style=for-the-badge" alt="PowerFactory">
</p>

<p>
  <a href="https://epowcore.readthedocs.io/">
    <img src="https://img.shields.io/badge/Documentation-ReadTheDocs-8CA1AF?style=flat-square&logo=readthedocs&logoColor=white" alt="Documentation">
  </a>
  <a href="https://doi.org/10.5281/zenodo.13827587">
    <img src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.13827587-1682D4?style=flat-square" alt="DOI">
  </a>
  <a href="https://github.com/KIT-IAI/ePowCoRe">
    <img src="https://img.shields.io/badge/GitHub-KIT--IAI%2FePowCoRe-181717?style=flat-square&logo=github" alt="GitHub">
  </a>
</p>

</div>

---

## 🌐 Overview

**ePowCoRe** provides a generic representation of electrical power-grid models and a modular framework for converting models between different simulation and modeling environments.

At the center of the project is the **Generic Data Format (GDF)**, which acts as a neutral intermediate representation between source and target platforms.

```text
┌──────────────────┐
│   Source Model   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│       GDF        │
│ Generic Data     │
│     Format       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Target Model   │
└──────────────────┘
```

This architecture keeps importers and exporters independent and makes conversion workflows easier to maintain and extend.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/KIT-IAI/ePowCoRe.git
cd ePowCoRe
```

### 2. Set up the environment with `uv`

The recommended development workflow uses [uv](https://docs.astral.sh/uv/) for dependency and environment management.

```bash
uv sync
```

This creates a local virtual environment:

```text
.venv
```

### 3. Activate the environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or run commands directly through `uv` without activating the environment:

```bash
uv run python --version
```

---

## 📦 Dependency Management

Project dependencies are defined in:

```text
pyproject.toml
```

Resolved dependency versions are stored in:

```text
uv.lock
```

After changing dependencies:

```bash
uv lock
uv sync
```

When dependency resolution changes, both `pyproject.toml` and `uv.lock` should normally be committed.

---

## 🧰 Development Setup

After cloning the repository, the standard setup is simply:

```bash
uv sync
```

Useful checks:

```bash
uv run python --version
uv run pytest --version
```

---

## 🖥️ VS Code

The repository provides recommended VS Code extensions and workspace settings.

### Recommended extensions

- 🎨 **Black Formatter**
- 🧹 **isort**
- ✍️ **autoDocstring**

Recommendations are stored in:

```text
.vscode/extensions.json
```

Workspace settings are stored in:

```text
.vscode/settings.json
```

These settings help keep formatting and import organization consistent across contributors.

---

## 🔄 Usage

Conversion and utility scripts are available in:

```text
scripts/
```

Example:

```bash
uv run python scripts/pf_to_jmdl.py
```

If the virtual environment is already activated:

```bash
python scripts/pf_to_jmdl.py
```

Depending on the script, input models, output paths, or conversion parameters may need to be configured before execution.

---

## 🔌 Supported Model Interfaces

ePowCoRe contains modules for several power-system and modeling environments.

| Interface | Purpose |
|---|---|
| 🧩 **GDF** | Generic internal representation |
| 🌍 **GeoJSON** | Geographic data representation |
| 🧱 **JMDL** | JMDL model conversion |
| 🧮 **MATPOWER** | MATPOWER-related conversion |
| ⚡ **pandapower** | Import, export, conversion and plausibility checks |
| 🏭 **PowerFactory** | DIgSILENT PowerFactory import/export |
| 🛰️ **RSCAD / RTDS** | RTDS-related integration |
| 🔬 **Simscape** | MATLAB Simscape integration |

> Support can vary depending on component type and conversion direction.

---

## 🗂️ Project Structure

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
│   ├── plausibility/
│   ├── power_factory/
│   ├── rscad/
│   └── simscape/
│
├── scripts/
├── tests/
├── tests_slow/
├── documentation/
├── pyproject.toml
├── uv.lock
└── README.md
```

### Core areas

| Directory | Description |
|---|---|
| `epowcore/gdf` | Generic Data Format, core model, components, connections and subsystems |
| `epowcore/generic` | Generic structures and platform-independent functionality |
| `epowcore/pandapower` | pandapower-specific conversion functionality |
| `epowcore/power_factory` | PowerFactory-specific conversion functionality |
| `epowcore/plausibility` | Post-export plausibility checks |
| `scripts` | Conversion and utility scripts |
| `tests` | Regular automated tests |
| `tests_slow` | Tests requiring additional software or longer-running environments |

---

## ⚡ pandapower

pandapower-related functionality is located in:

```text
epowcore/pandapower/
```

The exporter follows the pandapower 3.x API used by the project.

Related functionality includes:

- model conversion
- exported-network validation
- post-export plausibility checks
- result traceability
- isolated-area visualization

---

## 🏭 PowerFactory

PowerFactory-related functionality is located in:

```text
epowcore/power_factory/
```

Some PowerFactory functionality requires the DIgSILENT PowerFactory Python API to be installed and available in the active environment.

### Geographic data handling

When importing PowerFactory models, geographic coordinates are preserved where possible.

If a component has only default coordinates, it can inherit coordinates from supported parent objects such as:

- `ElmSite`
- `ElmSubstat`

Existing component coordinates are preserved when they are already defined.

---

## 🧪 Plausibility Checks

ePowCoRe includes post-export plausibility checks for supported target formats.

For pandapower exports, checks can include:

| Check | Purpose |
|---|---|
| ✅ Load-flow convergence | Verify that the exported model can be solved |
| 🔋 Bus voltage | Detect soft and hard voltage violations |
| ⚙️ Generator voltage | Detect generator voltage violations |
| 🔌 Line loading | Detect overloaded lines |
| 🔁 Transformer loading | Detect overloaded transformers |
| 🧭 Isolated areas | Detect disconnected network sections |
| 🗺️ Visualization | Plot isolated network areas |

Where geographic coordinates are available, network plots can use a geographic map background. Otherwise, available model coordinates are used for a schematic representation.

---

## 🧪 Testing

Run the regular test suite:

```bash
uv run pytest tests/
```

Run with concise output:

```bash
uv run pytest tests/ -q
```

### Focused test suites

pandapower:

```bash
uv run pytest tests/pandapower/
```

Plausibility:

```bash
uv run pytest tests/plausibility/
```

PowerFactory utilities:

```bash
uv run pytest tests/power_factory/utils_test.py -q
```

---

## 📊 Testing & Coverage

Run tests with coverage:

```bash
uv run pytest --cov=epowcore tests/
```

Generate an XML coverage report:

```bash
uv run coverage xml
```

### External dependencies

Some tests require software or APIs that are not available in every development environment.

Examples include:

- DIgSILENT PowerFactory
- MATLAB / Simscape
- RSCAD / RTDS-related dependencies

A complete local test run may therefore require additional installed software.

For development on a specific integration, use the corresponding focused test suite where appropriate.

---

## 🎨 Code Quality

The project uses standard Python formatting and import-organization tools.

### Black

```bash
uv run black epowcore tests
```

### isort

```bash
uv run isort epowcore tests
```

Before committing, check for whitespace problems:

```bash
git diff --check
```

---

## 📚 Documentation

Project documentation is available at:

### 👉 [epowcore.readthedocs.io](https://epowcore.readthedocs.io/)

The documentation source is located in:

```text
documentation/source/
```

### Build API documentation

```bash
uv run sphinx-apidoc -f -d 3 -E -o ./documentation/source/apidoc ./epowcore/ ./epowcore/generic ./epowcore/jmdl ./epowcore/power_factory/ ./epowcore/rscad/ ./epowcore/simscape/ ./epowcore/geojson/
```

### Build HTML documentation

```bash
uv run sphinx-build -b html documentation/source documentation/build/html -c ./documentation/source/
```

Generated files are written to:

```text
documentation/build/html/
```

---

## 🌿 Development Workflow

Create a branch from the latest `main`:

```bash
git checkout main
git pull
git checkout -b feature/my-change
```

Synchronize dependencies:

```bash
uv sync
```

Make the required changes and run the relevant tests:

```bash
uv run pytest tests/
```

Review the working tree:

```bash
git diff --check
git status
git diff
```

Commit:

```bash
git add .
git commit -m "describe the change"
```

Push:

```bash
git push -u origin feature/my-change
```

Then open a pull request against `main`.

---

## 🤝 Contributing

When contributing to ePowCoRe:

1. 🌱 Create a dedicated branch from the latest `main`.
2. 🎯 Keep changes focused on a single issue or feature.
3. 🧪 Add or update tests when behavior changes.
4. ✅ Run the relevant test suite locally.
5. 🧹 Run `git diff --check`.
6. 📦 Commit lock-file changes when dependencies change.
7. 📖 Update documentation when user-facing behavior changes.
8. 🔀 Open a pull request with a clear description.

---

## 📖 Citing

### Software

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.13827587.svg)](https://doi.org/10.5281/zenodo.13827587)

### Article

> M. Weber, A. Kocher, H. K. Çakmak and V. Hagenmeyer,  
> **"ePowCoRe: A Novel Generic Representation of Power Grids Enabling Open-Source Model Conversion Modules,"**  
> 2024 Open Source Modelling and Simulation of Energy Systems (OSMSES),  
> Vienna, Austria, 2024, pp. 1-6,  
> doi: `10.1109/OSMSES62085.2024.10668981`.

---

<div align="center">

### ⚡ ePowCoRe

**Generic power-grid models. Modular conversion. Open-source workflows.**

</div>