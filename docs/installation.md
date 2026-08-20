# Installation Guide

DocMergeForge is a Python 3.12+ application with CLI, PySide6 desktop, and optional responsive web entry points. This guide covers normal source installation, isolated environments, browser/mobile access, developer setup, Linux desktop prerequisites, verification, upgrades, and uninstallation.

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

## Responsive web installation

The browser interface lets Android, iOS/iPadOS, ChromeOS, and modern desktop browsers use a DocMergeForge Python host while reusing the same PDF and DOCX engines.

Install the optional web runtime:

```bash
pip install -e ".[web]"
```

Start the safest default, which binds only to the current computer:

```bash
docmergeforge-web
```

Then open:

```text
http://127.0.0.1:8765/
```

For another computer, phone, tablet, or Chromebook on the same trusted LAN, a non-loopback bind requires an access token:

```bash
docmergeforge-web --host 0.0.0.0 --token auto
```

The command prints a generated token and reminds you to open the host computer's LAN IP on port `8765`. Open that LAN address, enter the generated value in **Access token (LAN only)**, choose PDF/DOCX files, and merge normally.

A trusted one-time link can put the token in a URL fragment because fragments are not sent to the HTTP server:

```text
http://HOST-LAN-IP:8765/#token=YOUR_LONG_RANDOM_TOKEN
```

Do not use `?token=...`. Query parameters can be retained in HTTP access logs, proxies, browser history, or other infrastructure before the page has a chance to change its visible URL. The exact mobile/browser support and security boundaries are documented in [Platform Support](platform-support.md) and [Security Model](security.md).

The built-in web server is not intended to be directly exposed to the public Internet. Remote deployments need HTTPS, authentication, reverse-proxy hardening, and appropriate request limits.

## Developer installation

Install development and web-test dependencies:

```bash
pip install -e ".[dev,web]"
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
python scripts/check_docs_links.py
python scripts/check_repository_reference.py
pytest
```

The repository CI currently runs Quality checks on Python 3.12 and 3.13, including the responsive web/API tests.

## Packaging-tool installation

To build desktop executables, install the `build` extra:

```bash
pip install -e ".[build]"
```

Validate packaging configuration without building:

```bash
python scripts/build_desktop.py --check
```

See [Building Executables](building-executables.md) for complete native desktop platform instructions. The current Android/iOS path is browser-based; desktop PyInstaller packaging is not represented as an APK, AAB, or IPA build.

## Linux Qt runtime prerequisites

PySide6 wheels contain Qt, but a minimal Linux environment can still be missing system runtime libraries needed to load the GUI stack. The GitHub Ubuntu runners explicitly install `libegl1` before accessibility and GUI smoke checks.

On Debian/Ubuntu systems where importing PySide6 fails with `libEGL.so.1: cannot open shared object file`, install:

```bash
sudo apt-get update
sudo apt-get install -y libegl1
```

Desktop Linux distributions may already include this dependency. A headless web deployment does not display the PySide6 GUI, although the current base package still includes the desktop dependency set.

## Running without global installation

From an activated editable development environment, the normal entry points are preferred:

```bash
docmergeforge --help
docmergeforge-gui
docmergeforge-web --help
```

The package can also be invoked through Python where appropriate, but automation and documentation should use the installed console scripts so behavior matches packaged usage.

## Updating a source checkout

From the repository root:

```bash
git pull
python -m pip install --upgrade pip
pip install -e .
```

For a developer/browser-test environment:

```bash
pip install -e ".[dev,web]"
```

For a browser runtime:

```bash
pip install -e ".[web]"
```

For a packaging environment:

```bash
pip install -e ".[build]"
```

After a significant update, rerun:

```bash
docmergeforge --help
docmergeforge-web --help
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

Browser mode additionally needs temporary host storage for request uploads and the generated result until the response completes. The web server defaults to a 4096 MiB total upload limit per request; change it deliberately with `--max-upload-mib` when appropriate.

Project preflight calculates source, temporary, projected output, safe-required, and currently free bytes for project workflows. Treat a failed storage preflight as a blocking condition.

## Permissions

The output directory must be writable. Project preflight performs a writeability probe before expensive merge work. If the destination is read-only, protected by policy, on an unavailable network share, or otherwise inaccessible, fix the location or permissions rather than bypassing the check.

The browser interface uses a per-request temporary workspace on the Python host and removes it after the download response or after an error.

## Encrypted PDFs

Encrypted PDFs are supported only when the user provides a valid password during the run. Passwords are kept only for the active operation; they are not written into project files or normal diagnostics.

The CLI collects passwords interactively. The responsive web interface accepts one optional shared password for the PDFs in that browser merge request. If encrypted files use different passwords, use another supported workflow rather than persisting passwords in a project.

When browser traffic is not confined to loopback or a trusted LAN, use HTTPS so the PDF password, access token header, and manuscript upload are protected in transit.

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

- `python --version` reports 3.12+ on the Python host;
- `docmergeforge --help` works for CLI use;
- `docmergeforge-gui` starts when native desktop GUI use is required;
- `docmergeforge-web --help` works when browser/mobile access is required;
- non-loopback web binds use a strong access token and a trusted network;
- browser tokens are entered in the LAN-token field or passed in a `#token=...` fragment, never a query parameter;
- HTTPS protects browser traffic when it leaves a trusted local environment;
- the source folders are readable;
- the output/temp locations have sufficient free space;
- the correct project/preset and part range are selected;
- originals are backed up independently.
