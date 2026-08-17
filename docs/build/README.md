# Executable Build Documentation

This directory is the complete build and packaging manual for DocMergeForge desktop executables.

DocMergeForge currently uses **PyInstaller** through the repository helper `scripts/build_desktop.py`. The supported repository build modes are:

- **onedir** — default distribution/development build mode;
- **onefile** — optional single-file PyInstaller build with its own cross-platform acceptance workflow;
- **GitHub Actions unsigned native artifacts** — Windows, macOS, and Linux with packaged publication smoke and SHA-256 evidence.

The repository does **not** currently claim that Windows installers, macOS notarized releases, Linux distro-native packages, or signed production binaries are automatically produced. Those are documented as production distribution steps and remain separate acceptance gates.

> **Made by the Sanskar** · [Buy Me a Coffee](https://buymeacoffee.com/sanskarIN)

## Build documentation map

1. [Common Build Guide](common.md) — environment preparation, helper commands, build modes, clean builds, output layout, and common verification.
2. Native platform guide — [Windows](windows.md), [macOS](macos.md), or [Linux](linux.md).
3. [CI Packaging](ci-packaging.md) — current onedir Package Desktop workflow and artifact behavior.
4. [Build Provenance](provenance.md) — privacy-safe build/source/dependency metadata generator.
5. [Signing and Notarization](signing-and-notarization.md) — production trust requirements and safe credential handling.
6. [Executable Verification](verification.md) — build-host, downloaded-artifact, clean-machine, hash, and signature acceptance.
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

`.github/workflows/package.yml` builds the default onedir package on Windows/macOS/Ubuntu, runs the packaged mixed PDF+DOCX smoke on the build runner, archives it, creates a SHA-256 sidecar, and uploads it.

The workflow also has a **fresh-runner verification** matrix. These jobs do not check out the source repository or install the Python project/build environment. They download the uploaded archive, verify its SHA-256 sidecar, extract it, and execute `--packaged-smoke` again. Linux installs only the required system `libegl1` runtime prerequisite.

### Onefile Acceptance

`.github/workflows/onefile-acceptance.yml` independently builds `--one-file` on Windows/macOS/Ubuntu, runs the same real packaged publication smoke, archives/hashes/uploads each artifact, and then repeats downloaded-artifact verification on fresh runners.

Onedir and onefile are therefore treated as separate distribution surfaces rather than assuming that one mode proves the other.

## Development build versus production distribution

A successful PyInstaller/fresh-runner build still does not automatically equal production distribution.

Production acceptance additionally requires release identity, current source/security/recovery/stress/fidelity/accessibility evidence appropriate to the support claim, human interactive testing where required, and real signing/notarization when claimed.

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

Each automated archive has a matching `.sha256` sidecar. These names are intentionally explicit; do not rename unsigned artifacts to imply signed production trust.

## Build provenance

The reusable provenance generator is implemented in:

```text
src/docmergeforge/packaging/provenance.py
scripts/write_build_provenance.py
```

It records allowlisted source/CI/build/dependency metadata without dumping environment secrets or manuscript paths. See [Build Provenance](provenance.md).

The generator is a reusable primitive; workflow integration should only be claimed after the artifact workflows actually generate/upload/verify its output.

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
src/docmergeforge/packaging/desktop.py
src/docmergeforge/packaging/provenance.py
src/docmergeforge/ui/packaged_entry.py
pyproject.toml
.github/workflows/package.yml
.github/workflows/onefile-acceptance.yml
```

Documentation is intentionally conservative: if these files do not implement a packaging feature, this manual does not claim that feature is already automated.

## Related documentation

- [Building Executables overview](../building-executables.md)
- [Release Packaging](../release-packaging.md)
- [Release Process](../release-process.md)
- [Testing and CI](../testing-and-ci.md)
- [Security Model](../security.md)
- [Known Limitations](../known-limitations.md)
