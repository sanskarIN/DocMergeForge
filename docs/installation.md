# Installation Guide

DocMergeForge is a Python 3.12+ application with both CLI and PySide6 desktop entry points. This guide covers normal source installation, isolated environments, developer setup, Linux desktop prerequisites, verification, upgrades, and uninstallation.

## Requirements

Minimum source-install requirements:

- Python 3.12 or newer.
- `pip` available for that Python installation.
- Enough local storage for source documents, temporary merge files, final outputs, reports, and rollback staging.
- A writable output location.

Core Python dependencies are declared in `pyproject.toml` and include `pypdf`, `python-docx`, `docxcompose`, `PySide6`, and `reportlab`.

## Recommended isolated installation

Clone the repository and create a virtual environment.

```bash
git clone https://github.com/sanskarIN/DocMergeForge.git
cd DocMergeForge
python -m venv .venv
```

Activate it.

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```bat
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Upgrade packaging tools and install DocMergeForge.

```bash
python -m pip install --upgrade pip
pip install -e .
```

## Verify the installation

Verify the CLI:

```bash
docmergeforge --help
```

Verify the desktop entry point:

```bash
docmergeforge-gui
```

Verify the package import:

```bash
python -c "import docmergeforge; print('DocMergeForge import OK')"
```

## Developer installation

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Install pre-commit hooks:

```bash
pre-commit install
```

Run the standard checks:

```bash
ruff check .
black --check .
mypy src/docmergeforge
pytest
```

The repository CI currently runs Quality checks on Python 3.12 and 3.13.

## Packaging-tool installation

To build desktop executables, install the `build` extra:

```bash
pip install -e ".[build]"
```

Validate packaging configuration without building:

```bash
python scripts/build_desktop.py --check
```

See [Building Executables](building-executables.md) for complete platform instructions.

## Linux Qt runtime prerequisites

PySide6 wheels contain Qt, but a minimal Linux environment can still be missing system runtime libraries needed to load the GUI stack. The GitHub Ubuntu runners explicitly install `libegl1` before accessibility and GUI smoke checks.

On Debian/Ubuntu systems where importing PySide6 fails with `libEGL.so.1: cannot open shared object file`, install:

```bash
sudo apt-get update
sudo apt-get install -y libegl1
```

Desktop Linux distributions may already include this dependency.

## Running without global installation

From an activated editable development environment, the normal entry points are still preferred:

```bash
docmergeforge --help
docmergeforge-gui
```

The package can also be invoked through Python where appropriate, but automation and documentation should use the installed console scripts so behavior matches packaged usage.

## Updating a source checkout

From the repository root:

```bash
git pull
python -m pip install --upgrade pip
pip install -e .
```

For a developer environment:

```bash
pip install -e ".[dev]"
```

For a packaging environment:

```bash
pip install -e ".[build]"
```

After a significant update, rerun:

```bash
docmergeforge --help
python scripts/build_desktop.py --check
```

## Storage planning

Do not size storage only for the final merged manuscript. A safe run may need space for:

- original source files;
- temporary PDF/DOCX outputs;
- staged final outputs;
- generated reports and checksums;
- transaction backups of existing published outputs when overwrite is enabled;
- operating-system and filesystem overhead.

Project preflight calculates source, temporary, projected output, safe-required, and currently free bytes. Treat a failed storage preflight as a blocking condition.

## Permissions

The output directory must be writable. Project preflight performs a writeability probe before expensive merge work. If the destination is read-only, protected by policy, on an unavailable network share, or otherwise inaccessible, fix the location or permissions rather than bypassing the check.

## Encrypted PDFs

Encrypted PDFs are supported only when the user provides a valid password during the run. Passwords are collected interactively and kept in memory for the active operation; they are not written into project files or normal diagnostics.

For non-interactive automation involving encrypted PDFs, design the surrounding workflow carefully because the current CLI password collection is interactive.

## Optional high-fidelity office suites

Portable DOCX composition is the production-supported mode in the current repository. LibreOffice and Microsoft Word fidelity modes may be detected as capabilities, but their automation adapters are not yet accepted as production-ready and must not be treated as transparent fallbacks.

Installing LibreOffice or Microsoft Word does not by itself make those DocMergeForge fidelity modes complete.

## Uninstallation

If installed into a virtual environment, deactivate and delete the environment after preserving any needed project/output files.

```bash
deactivate
```

Then remove `.venv` using your operating system.

If installed into another Python environment:

```bash
pip uninstall docmergeforge
```

Removing the Python package does not delete your source manuscripts, output folders, or project files.

## Installation checklist

Before starting production work, confirm:

- `python --version` reports 3.12+;
- `docmergeforge --help` works;
- `docmergeforge-gui` starts when GUI use is required;
- the source folders are readable;
- the output folder is writable and has sufficient free space;
- the correct project/preset and part range are selected;
- originals are backed up independently.
