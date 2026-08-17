# Building Executables

DocMergeForge includes a reproducible PyInstaller helper for producing desktop development builds on Windows, macOS, and Linux. The default build is an **onedir** application; an optional **one-file** build is also supported.

The current packaging foundation creates unsigned development artifacts. Signing, notarization, installer creation, and final distribution acceptance are separate release steps.

## Supported build hosts

The repository packaging matrix currently targets:

- Windows (`windows-latest`);
- macOS (`macos-latest`);
- Linux (`ubuntu-latest`).

Build each platform artifact on its native platform/runner. PyInstaller is not a general cross-compiler: a Windows host should build the Windows app, macOS should build macOS, and Linux should build Linux.

## Requirements

- Python 3.12 recommended for parity with packaging CI.
- Repository checkout containing `pyproject.toml`.
- `src/docmergeforge/ui/main.py` present.
- Build dependencies installed.
- Platform runtime/build prerequisites available.

## Prepare a clean environment

From the repository root:

```bash
python -m venv .venv
```

Activate the environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install packaging dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[build]"
```

This installs the application plus PyInstaller through the declared `build` optional dependency.

## Always run packaging preflight first

```bash
python scripts/build_desktop.py --check
```

Expected success message:

```text
Desktop build configuration OK: <repository-root>
```

The preflight verifies the build root contains required repository inputs rather than failing later inside PyInstaller.

You can validate another checkout/root explicitly:

```bash
python scripts/build_desktop.py --check --root "/path/to/DocMergeForge"
```

## Default onedir build

Run:

```bash
python scripts/build_desktop.py
```

The helper constructs PyInstaller arguments for:

- entry point `src/docmergeforge/ui/main.py`;
- app name `DocMergeForge`;
- windowed mode;
- clean/noninteractive build;
- `docmergeforge` submodule collection;
- `docxcompose`, `docx`, and `pypdf` data/submodule collection;
- `assets/branding` inclusion when present;
- `--onedir` output by default.

Typical generated locations:

```text
build/
dist/DocMergeForge/
```

The exact executable/bundle structure is platform-specific.

## One-file build

```bash
python scripts/build_desktop.py --one-file
```

This replaces `--onedir` with PyInstaller `--onefile`.

One-file packaging can have different startup/runtime extraction behavior. Treat it as a separate acceptance target and test it on the real OS rather than assuming parity with onedir.

## Windows build

### Local build

PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[build]"
python scripts/build_desktop.py --check
python scripts/build_desktop.py
```

Then inspect:

```text
dist\DocMergeForge\
```

Launch the generated executable from a normal non-admin account.

### Windows acceptance checklist

- app starts without a console window unexpectedly appearing;
- branding assets load;
- create/open project works;
- file/folder dialogs work;
- PDF merge works;
- DOCX merge works;
- encrypted PDF prompt works;
- reports open/display;
- cancellation/recovery path works;
- long/Unicode/space-containing paths work;
- app works from a non-development machine or clean VM;
- Windows Defender/SmartScreen behavior is reviewed;
- final installer/executable is code-signed before production distribution.

### Windows installer

The repository currently builds a PyInstaller directory/archive foundation, not a finished signed installer format such as MSI/MSIX/Inno Setup/NSIS.

If a production installer is added later, document and test:

- install/uninstall;
- per-user/per-machine choice;
- shortcuts;
- upgrade/downgrade behavior;
- file associations if any;
- code signing;
- clean removal without deleting user manuscripts/projects.

## macOS build

### Local build

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[build]"
python scripts/build_desktop.py --check
python scripts/build_desktop.py
```

Inspect `dist/DocMergeForge` and the generated macOS bundle/layout produced by the active PyInstaller version/configuration.

### macOS acceptance checklist

- launch from Finder and terminal;
- Gatekeeper behavior reviewed;
- file dialogs work;
- app can read/write intended folders under macOS privacy controls;
- PDF/DOCX workflows pass;
- Unicode/long paths pass;
- Apple Silicon target is tested where required;
- Intel target/universal strategy is explicitly decided if required;
- app is signed with the intended Developer ID identity;
- hardened runtime/entitlements are reviewed;
- notarization succeeds;
- stapling/verification succeeds;
- a clean Mac accepts/launches the distributed build.

### Signing/notarization

The current repository does **not** claim macOS signing/notarization. Production distribution should add a credential-secured release pipeline rather than embedding signing secrets in the repository.

## Linux build

### Local build

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[build]"
python scripts/build_desktop.py --check
python scripts/build_desktop.py
```

On Debian/Ubuntu, if PySide6 fails to import due to missing EGL runtime:

```bash
sudo apt-get update
sudo apt-get install -y libegl1
```

### Linux acceptance checklist

- test on the minimum supported distro/glibc baseline you intend to claim;
- launch in a normal graphical session;
- check Qt platform plugins;
- verify `libEGL`/graphics runtime availability;
- test file dialogs/paths;
- test PDF/DOCX workflows;
- test Wayland/X11 environments where relevant;
- verify permissions on mounted/removable filesystems;
- decide distribution format (tarball/AppImage/deb/rpm/etc.) explicitly;
- document runtime compatibility instead of assuming a binary built on a new distro works everywhere.

The current CI artifact is a tar.gz of the PyInstaller `dist/DocMergeForge` directory, not a distro-native package.

## GitHub Actions Package Desktop workflow

The repository provides `.github/workflows/package.yml`.

Triggers:

- manual `workflow_dispatch`;
- pushes of tags matching `v*`.

It runs a matrix on Windows, macOS, and Ubuntu using Python 3.12.

Workflow stages:

1. checkout;
2. setup Python/pip cache;
3. install `.[build]`;
4. run `python scripts/build_desktop.py --check`;
5. run `python scripts/build_desktop.py`;
6. archive the platform output;
7. upload an unsigned artifact.

Current archive names:

```text
DocMergeForge-Windows-unsigned.zip
DocMergeForge-macOS-unsigned.tar.gz
DocMergeForge-Linux-unsigned.tar.gz
```

Artifact names explicitly include `unsigned` so they cannot be confused with production-signed releases.

## Build Smoke versus Package Desktop

### Build Smoke

Runs cross-platform source/import/accessibility/packaging **preflight** checks. It does not produce final release packages.

### Package Desktop

Actually invokes PyInstaller and uploads development artifacts.

### Production release acceptance

Must additionally verify signing/notarization/installer behavior and real packaged-app launch/merge workflows.

## Clean rebuilds

The PyInstaller helper already uses `--clean` and `--noconfirm`, but when investigating strange packaging behavior it can be useful to remove local generated directories first:

Windows PowerShell:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
```

macOS/Linux:

```bash
rm -rf build dist
```

Then reinstall/update dependencies if needed and rebuild.

Do not delete source/output manuscript folders when cleaning packaging artifacts.

## Build from a specific repository root

The helper supports:

```bash
python scripts/build_desktop.py --root "/path/to/repo"
```

Preflight requires at least:

```text
<root>/pyproject.toml
<root>/src/docmergeforge/ui/main.py
```

An invalid root exits with a clear missing-input message.

## Branding assets

If `assets/branding` exists, the build helper adds it to the package data under:

```text
assets/branding
```

Keep asset paths stable or update packaging/resource-loading tests together.

## Debugging packaging failures

### `PyInstaller is required`

Install:

```bash
pip install -e ".[build]"
```

### Invalid build root

Run:

```bash
python scripts/build_desktop.py --check --root <path>
```

Confirm `pyproject.toml` and `src/docmergeforge/ui/main.py` exist.

### PySide6/Qt runtime failure on Linux

Install the missing system runtime such as `libegl1`, then rerun the import/smoke/build.

### App builds but fails on launch

Test from terminal where possible to capture diagnostics. Check:

- missing Qt plugin/library;
- missing bundled Python package/data;
- incorrect resource path;
- unsupported OS/runtime baseline;
- permissions;
- packaging hidden imports/submodule collection.

Fix the shared build configuration in `src/docmergeforge/packaging/desktop.py` so local/CI builds use the same solution.

## Reproducibility notes

The helper centralizes PyInstaller arguments, which reduces configuration drift, but fully bit-for-bit reproducible binaries are not currently claimed. Build output can vary with:

- OS image;
- Python patch version;
- dependency versions;
- PyInstaller version;
- filesystem metadata;
- signing/notarization timestamps.

For releases, record exact commit/tag, workflow run, dependency environment, and artifact hashes.

## Production packaging checklist

Before calling an executable production-ready:

- Quality CI green at release head;
- 120-Part Regression green;
- Build Smoke green on all target OSes;
- Security/CodeQL green;
- PyInstaller package built on each target OS;
- packaged app launched on clean target machines;
- representative PDF/DOCX project merge succeeds in packaged app;
- cancellation/recovery tested;
- accessibility smoke/manual checks completed;
- real-world fidelity acceptance completed;
- stress acceptance appropriate to claimed scale completed;
- Windows signing verified;
- macOS signing/notarization verified;
- Linux distribution compatibility verified;
- release checksums generated/published;
- no artifact labeled `unsigned` is presented as signed.

See [Release Process](release-process.md) for the end-to-end release gate.
