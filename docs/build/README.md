# Executable Build Documentation

This directory is the complete build and packaging manual for DocMergeForge desktop executables.

DocMergeForge currently uses **PyInstaller** through the repository helper `scripts/build_desktop.py`. The supported repository build modes are:

- **onedir** — default distribution/development build mode;
- **onefile** — optional single-file PyInstaller build with its own cross-platform acceptance workflow;
- **GitHub Actions unsigned native artifacts** — Windows, macOS, and Linux with packaged publication smoke, SHA-256, archive-bound provenance, and independent fresh-runner verification.

The repository does **not** currently claim that Windows installers, macOS notarized releases, Linux distro-native packages, or signed production binaries are automatically produced. Those are documented as production distribution steps and remain separate acceptance gates.

> **Made by the Sanskar** · [Buy Me a Coffee](https://buymeacoffee.com/sanskarIN)

## Build documentation map

1. [Common Build Guide](common.md) — environment preparation, helper commands, build modes, clean builds, output layout, and common verification.
2. Native platform guide — [Windows](windows.md), [macOS](macos.md), or [Linux](linux.md).
3. [CI Packaging](ci-packaging.md) — current onedir Package Desktop workflow and artifact behavior.
4. [Build Provenance](provenance.md) — privacy-safe source/build/dependency metadata bound to exact archive bytes.
5. [Signing and Notarization](signing-and-notarization.md) — production trust requirements and safe credential handling.
6. [Executable Verification](verification.md) — build-host, downloaded-artifact, human clean-machine, hash, provenance, and signature acceptance.
7. [Build Troubleshooting](troubleshooting.md) — packaging/import/resource/Qt/runtime failures.
8. [Release Build Checklist](release-checklist.md) — repeatable final checklist before publishing any executable.

## Canonical repository build commands

From the repository root after installing `.[build]`:

```bash
python scripts/build_desktop.py --check
python scripts/build_desktop.py
```

Optional one-file build:

```bash
python scripts/build_desktop.py --one-file
```

Explicit repository root:

```bash
python scripts/build_desktop.py --check --root /path/to/DocMergeForge
python scripts/build_desktop.py --root /path/to/DocMergeForge
```

## What the helper currently packages

The shared configuration in `src/docmergeforge/packaging/desktop.py` currently tells PyInstaller to:

- use `src/docmergeforge/ui/packaged_entry.py` as the PyInstaller entry point;
- delegate normal packaged launches to the existing desktop `ui.main` behavior;
- expose `--packaged-smoke` for deterministic CI acceptance without changing normal `docmergeforge-gui` behavior;
- name the application `DocMergeForge`;
- build in windowed mode;
- clean old PyInstaller analysis state;
- run non-interactively;
- collect `docmergeforge` submodules;
- collect `docxcompose`, `docx`, and `pypdf` package data/submodules;
- include `assets/branding` when that directory exists;
- build `--onedir` by default or `--onefile` when requested.

If packaging behavior changes, update both the shared packaging code and this documentation.

## Native-build rule

PyInstaller is not used here as a general cross-compiler. Build each target on its native OS or a matching CI runner:

| Target | Build host |
|---|---|
| Windows | Windows |
| macOS | macOS |
| Linux | Linux |

Do not describe a Windows executable built on Linux, or a macOS application built on Windows, as a supported repository path unless a separate cross-compilation system is deliberately implemented and tested.

## CI acceptance layers

### Package Desktop — onedir

`.github/workflows/package.yml` builds the default onedir package on Windows/macOS/Ubuntu. Each build job:

1. validates packaging configuration;
2. creates the native PyInstaller application;
3. runs the packaged mixed PDF+DOCX smoke on the build host;
4. archives the application;
5. creates a SHA-256 sidecar;
6. creates privacy-safe provenance bound to archive filename, byte size, and SHA-256;
7. uploads archive, sidecar, and provenance together.

The workflow then runs a separate **fresh-runner verification** matrix. Those jobs do not check out the repository or install DocMergeForge/Python project dependencies. They download the uploaded artifact, verify source/build/trust/archive provenance, recompute archive SHA-256/size, verify the `.sha256` sidecar, extract the archive, and execute `--packaged-smoke` again. Linux installs only the required system `libegl1` runtime prerequisite.

Verified archive-bound run:

```text
Package Desktop: 32025126032
Checkpoint: 59107192d494d76a4112cdeaa9a55f01cfe37972
Windows/macOS/Ubuntu build jobs: PASS
Windows/macOS/Ubuntu fresh-runner jobs: PASS
```

### Onefile Acceptance

`.github/workflows/onefile-acceptance.yml` independently builds `--one-file` on Windows/macOS/Ubuntu and applies the same build-host publication smoke, archive/checksum/provenance upload, and fresh-runner archive-bound verification model.

Verified archive-bound run:

```text
Onefile Acceptance: 32025167433
Checkpoint: b8a181b7138a1bc617766dd3e86c9ab32aade75e
Windows/macOS/Ubuntu build jobs: PASS
Windows/macOS/Ubuntu fresh-runner jobs: PASS
```

Onedir and onefile are therefore verified as separate distribution surfaces rather than assuming that one mode proves the other.

## Development build versus production distribution

A successful PyInstaller/fresh-runner build still does not automatically equal production distribution.

Production acceptance additionally requires current source/security/recovery/stress/fidelity/accessibility evidence appropriate to the support claim, human interactive testing on representative clean machines, and real signing/notarization when claimed.

## Current unsigned artifact families

Onedir:

```text
DocMergeForge-Windows-unsigned.zip
DocMergeForge-macOS-unsigned.tar.gz
DocMergeForge-Linux-unsigned.tar.gz
```

Onefile:

```text
DocMergeForge-Windows-onefile-unsigned.zip
DocMergeForge-macOS-onefile-unsigned.tar.gz
DocMergeForge-Linux-onefile-unsigned.tar.gz
```

Each automated archive has matching evidence:

```text
<archive>.sha256
<artifact-label>.provenance.json
```

These names are intentionally explicit. Do not rename unsigned artifacts to imply signed production trust.

## Build provenance

The verified provenance implementation is:

```text
src/docmergeforge/packaging/provenance.py
scripts/write_build_provenance.py
```

It records allowlisted source/CI/build/dependency metadata without dumping environment secrets or manuscript paths, and binds CI provenance to the exact archive filename/size/SHA-256. Fresh runners recompute and validate those values before executing the downloaded package.

See [Build Provenance](provenance.md) for the exact verified run/artifact evidence.

## Output directories

PyInstaller normally uses repository-local generated directories including:

```text
build/
dist/
```

The exact internal output shape varies by platform and build mode. Always inspect the actual `dist` output on the target OS rather than assuming one platform's layout applies to another.

## Build source of truth

Current implementation sources include:

```text
scripts/build_desktop.py
scripts/write_build_provenance.py
src/docmergeforge/packaging/desktop.py
src/docmergeforge/packaging/provenance.py
src/docmergeforge/ui/packaged_entry.py
pyproject.toml
.github/workflows/package.yml
.github/workflows/onefile-acceptance.yml
```

Documentation is intentionally conservative: if these files do not implement and verify a packaging feature, this manual does not claim that feature is already automated.

## Current remaining executable release gates

Automated native build/download/extract/execute and archive-bound provenance are verified for onedir and onefile. Remaining production-oriented gates include:

- human interactive clean-machine testing;
- representative real-world PDF/DOCX fidelity review;
- human accessibility acceptance;
- measured multi-gigabyte stress appropriate to scale claims;
- Windows production signing/SmartScreen review where distributed;
- macOS Developer ID signing/notarization/stapling where distributed;
- intentional installer/container formats and their acceptance;
- final post-signing/post-notarization hashes and trust verification.

## Related documentation

- [Building Executables overview](../building-executables.md)
- [Release Packaging](../release-packaging.md)
- [Release Process](../release-process.md)
- [Testing and CI](../testing-and-ci.md)
- [Security Model](../security.md)
- [Known Limitations](../known-limitations.md)
