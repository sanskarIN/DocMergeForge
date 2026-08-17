# Executable Build Documentation

This directory is the complete build and packaging manual for DocMergeForge desktop executables.

DocMergeForge currently uses **PyInstaller** through the repository helper `scripts/build_desktop.py`. The supported repository build modes are:

- **onedir** — default, recommended for development and platform acceptance;
- **onefile** — optional single-file PyInstaller build;
- **GitHub Actions unsigned onedir artifacts** — Windows, macOS, and Linux through `.github/workflows/package.yml`.

The repository does **not** currently claim that Windows installers, macOS notarized releases, Linux distro-native packages, or signed production binaries are automatically produced. Those are documented as production distribution steps and remain separate acceptance gates.

> **Made by the Sanskar** · [Buy Me a Coffee](https://buymeacoffee.com/sanskarIN)

## Build documentation map

### Start here

1. [Common Build Guide](common.md) — environment preparation, build helper, build modes, clean builds, output layout, and common verification.
2. Choose the native platform guide:
   - [Windows](windows.md)
   - [macOS](macos.md)
   - [Linux](linux.md)
3. [CI Packaging](ci-packaging.md) — current Package Desktop workflow and artifact behavior.
4. [Signing and Notarization](signing-and-notarization.md) — production trust requirements and safe credential handling.
5. [Executable Verification](verification.md) — clean-machine launch, merge acceptance, hashes, signatures, and artifact evidence.
6. [Build Troubleshooting](troubleshooting.md) — packaging/import/resource/Qt/runtime failures.
7. [Release Build Checklist](release-checklist.md) — repeatable final checklist before publishing any executable.

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

- use `src/docmergeforge/ui/main.py` as the desktop entry point;
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

## Development build versus production distribution

A successful PyInstaller build proves only that an executable bundle was produced. Production distribution requires additional evidence.

### Development build

A development build may be:

- unsigned;
- produced from a local checkout or CI;
- used for functional testing;
- distributed only with clear `unsigned` labeling when appropriate.

### Production distribution

A production candidate should additionally have:

- a release commit/tag;
- green Quality, Regression, Build Smoke, and Security checks;
- clean-machine packaged-app launch tests;
- representative PDF and DOCX merge tests from the packaged application;
- recovery/cancellation acceptance;
- platform compatibility evidence;
- release hashes;
- verified Windows code signing where Windows trust is claimed;
- verified macOS Developer ID signing/notarization where macOS production distribution is claimed;
- documented Linux runtime/distribution compatibility;
- no embedded signing secrets in source control.

## Current CI artifacts

`.github/workflows/package.yml` currently creates unsigned development archives named:

```text
DocMergeForge-Windows-unsigned.zip
DocMergeForge-macOS-unsigned.tar.gz
DocMergeForge-Linux-unsigned.tar.gz
```

These names are intentionally explicit. Do not rename an unsigned artifact to imply that it is signed.

## Output directories

PyInstaller normally uses repository-local generated directories including:

```text
build/
dist/
```

The exact internal output shape varies by platform and build mode. Always inspect the actual `dist` output on the target OS rather than assuming one platform's layout applies to another.

## Build source of truth

For current implementation details, the build source of truth is:

```text
scripts/build_desktop.py
src/docmergeforge/packaging/desktop.py
pyproject.toml
.github/workflows/package.yml
```

Documentation is intentionally conservative: if these files do not implement a packaging feature, this manual does not claim that feature is already automated.

## Related documentation

- [Building Executables overview](../building-executables.md)
- [Release Packaging](../release-packaging.md)
- [Release Process](../release-process.md)
- [Testing and CI](../testing-and-ci.md)
- [Security Model](../security.md)
- [Known Limitations](../known-limitations.md)
