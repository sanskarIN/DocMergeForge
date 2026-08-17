# Building Executables

This is the canonical entry point for building DocMergeForge desktop executable artifacts.

The complete executable-build manual is split into focused guides under [`docs/build/`](build/README.md) so platform-specific details, signing requirements, verification, and troubleshooting are not compressed into a single page.

> **Made by the Sanskar** · [Buy Me a Coffee](https://buymeacoffee.com/sanskarIN)

## Complete manual

Follow these in order:

1. [Executable Build Documentation Portal](build/README.md)
2. [Common Build Guide](build/common.md)
3. Native platform:
   - [Windows Build Guide](build/windows.md)
   - [macOS Build Guide](build/macos.md)
   - [Linux Build Guide](build/linux.md)
4. [CI Packaging Guide](build/ci-packaging.md)
5. [Signing and Notarization](build/signing-and-notarization.md)
6. [Executable Verification](build/verification.md)
7. [Build Troubleshooting](build/troubleshooting.md)
8. [Release Build Checklist](build/release-checklist.md)

## Repository-supported build modes

DocMergeForge currently uses PyInstaller through:

```text
scripts/build_desktop.py
src/docmergeforge/packaging/desktop.py
```

Supported repository build modes:

- `--onedir` by default;
- `--onefile` through `--one-file`;
- unsigned GitHub Actions onedir archives for Windows/macOS/Linux.

Production code signing, macOS notarization, and native installer/package formats are documented release steps but are not currently automated repository claims.

## Minimum local build

From a clean repository checkout:

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

Install:

```bash
python -m pip install --upgrade pip
pip install -e ".[build]"
```

Run packaging preflight:

```bash
python scripts/build_desktop.py --check
```

Build recommended onedir artifact:

```bash
python scripts/build_desktop.py
```

Optional one-file:

```bash
python scripts/build_desktop.py --one-file
```

## Exact current packaging intent

The shared helper currently configures PyInstaller to:

- use `src/docmergeforge/ui/main.py`;
- name the application `DocMergeForge`;
- use windowed mode;
- use clean/noninteractive packaging;
- collect all `docmergeforge` submodules;
- collect `docxcompose`, `docx`, and `pypdf` package content;
- include `assets/branding` when present;
- emit onedir by default or onefile when selected.

## Build natively

PyInstaller is not treated as a general cross-compiler in this project.

| Target | Supported build host/runner |
|---|---|
| Windows | Windows |
| macOS | macOS |
| Linux | Linux |

Use the platform guide for exact commands and acceptance requirements.

## What a successful PyInstaller command proves

It proves that PyInstaller completed on that build host.

It does **not** by itself prove:

- the artifact launches on a clean machine;
- PDF/DOCX merging works from the packaged app;
- recovery works from the packaged app;
- onefile behaves like onedir;
- Windows Authenticode signing is valid;
- macOS Developer ID/notarization is valid;
- Linux runtime compatibility spans all distributions;
- an installer/package works;
- the artifact is ready for stable release.

Use [Executable Verification](build/verification.md) before distribution.

## Current CI packaging

Workflow:

```text
.github/workflows/package.yml
```

Triggers:

- manual `workflow_dispatch`;
- tags matching `v*`.

Current matrix:

```text
windows-latest / Python 3.12
macos-latest   / Python 3.12
ubuntu-latest  / Python 3.12
```

Current development artifact names:

```text
DocMergeForge-Windows-unsigned.zip
DocMergeForge-macOS-unsigned.tar.gz
DocMergeForge-Linux-unsigned.tar.gz
```

They are intentionally labeled **unsigned**.

See [CI Packaging Guide](build/ci-packaging.md).

## Production trust

### Windows

A signed production claim requires an actual Authenticode signing identity, signing operation, timestamping where applicable, signature verification, and final artifact hash.

### macOS

A signed/notarized production claim requires actual Developer ID signing, bundle verification, notarization, Gatekeeper acceptance, and final artifact hash after all transformations.

### Linux

At minimum publish and verify final artifact hashes. Any package/repository signature must be implemented and verified before it is claimed.

See [Signing and Notarization](build/signing-and-notarization.md).

## Native installers/packages

The repository does not currently automate these formats:

- Windows MSI/MSIX/Inno Setup/NSIS;
- macOS DMG/PKG;
- Linux AppImage/DEB/RPM/Flatpak/Snap.

If one is added, it becomes a distinct maintained build target with install/update/uninstall/signing/compatibility tests. The current PyInstaller archive must not be mislabeled as one of these formats.

## Clean build commands

Windows PowerShell:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
python scripts/build_desktop.py --check
python scripts/build_desktop.py
```

macOS/Linux:

```bash
rm -rf build dist
python scripts/build_desktop.py --check
python scripts/build_desktop.py
```

Only remove generated build directories. Never point cleanup at manuscript/source/output folders.

## Final hashes

Windows:

```powershell
Get-FileHash <artifact> -Algorithm SHA256
```

macOS:

```bash
shasum -a 256 <artifact>
```

Linux:

```bash
sha256sum <artifact>
```

Generate release hashes from the exact final distributed files after any byte-changing signing/notarization/container steps.

## Required release evidence

For each target executable retain:

- commit/tag;
- OS/architecture;
- Python/PyInstaller versions;
- build mode;
- CI run ID if applicable;
- final artifact filename/size/SHA-256;
- clean-machine launch result;
- packaged PDF merge result;
- packaged DOCX merge result;
- cancellation/recovery result;
- signature/notarization verification when claimed;
- installer/package acceptance when distributed;
- known limitations.

Use the [Release Build Checklist](build/release-checklist.md) as the go/no-go record.

## Current status

The repository has a reproducible shared PyInstaller configuration, cross-platform build preflight, cross-platform Build Smoke, and an unsigned Package Desktop workflow foundation.

It does **not** currently claim signed/notarized production binaries or stable `v1.0.0` package acceptance. Those remain release gates documented in the build and release manuals.

## Related documentation

- [Release Packaging](release-packaging.md)
- [Release Process](release-process.md)
- [Testing and CI](testing-and-ci.md)
- [Known Limitations](known-limitations.md)
- [Security Model](security.md)
- [Complete documentation index](README.md)
