# Release Packaging

DocMergeForge has a cross-platform PyInstaller packaging foundation and GitHub Actions workflow. The current workflow produces **unsigned development archives**. Production signing, notarization, installer creation, and clean-machine acceptance remain explicit release gates.

For command-by-command local builds, see [Building Executables](building-executables.md). For the complete acceptance sequence, see [Release Process](release-process.md).

## Shared packaging configuration

Packaging arguments live in:

```text
src/docmergeforge/packaging/desktop.py
```

The build script:

```text
scripts/build_desktop.py
```

imports that shared configuration. This avoids having tests, local builds, and CI each maintain a different PyInstaller argument list.

## Build-root validation

Before importing/running PyInstaller, the helper validates the repository root.

Required inputs currently include:

```text
pyproject.toml
src/docmergeforge/ui/main.py
```

Run:

```bash
python scripts/build_desktop.py --check
```

A bad root fails early with a list of missing required paths.

## PyInstaller configuration

The shared builder currently configures:

- entry point: `src/docmergeforge/ui/main.py`;
- app name: `DocMergeForge`;
- windowed desktop mode;
- clean build;
- noninteractive overwrite (`--noconfirm`);
- collection of `docmergeforge` submodules;
- full collection for `docxcompose`, `docx`, and `pypdf`;
- inclusion of `assets/branding` when present;
- `--onedir` by default;
- `--onefile` when explicitly requested.

## Local packaging

Install:

```bash
pip install -e ".[build]"
```

Preflight:

```bash
python scripts/build_desktop.py --check
```

Onedir:

```bash
python scripts/build_desktop.py
```

One-file:

```bash
python scripts/build_desktop.py --one-file
```

PyInstaller normally writes local build state under:

```text
build/
dist/
```

## GitHub Actions workflow

Workflow:

```text
.github/workflows/package.yml
```

Name:

```text
Package Desktop
```

Triggers:

- manual workflow dispatch;
- tags matching `v*`.

Matrix:

- `windows-latest`;
- `macos-latest`;
- `ubuntu-latest`;
- Python 3.12.

## Workflow steps

For each platform, Package Desktop currently:

1. checks out the repository;
2. sets up Python 3.12 with pip cache;
3. upgrades pip;
4. installs `pip install -e ".[build]"`;
5. validates packaging configuration;
6. runs the PyInstaller build helper;
7. archives `dist/DocMergeForge`;
8. uploads the platform artifact;
9. prints an explicit unsigned-development-build notice.

## Current CI artifact names

Windows:

```text
DocMergeForge-Windows-unsigned.zip
```

macOS:

```text
DocMergeForge-macOS-unsigned.tar.gz
```

Linux:

```text
DocMergeForge-Linux-unsigned.tar.gz
```

Uploaded GitHub Actions artifact labels likewise contain `unsigned`.

This naming is intentional to prevent accidental claims that CI archives have platform trust signatures.

## Windows distribution status

Current foundation:

- PyInstaller application directory;
- ZIP archive in CI.

Not yet claimed as completed production distribution:

- signed executable;
- MSI/MSIX/Inno/NSIS installer;
- installer signing;
- SmartScreen reputation acceptance;
- clean-machine install/upgrade/uninstall matrix.

A future Windows installer must preserve user manuscripts/projects during uninstall and should not require Administrator privileges without a real need.

## macOS distribution status

Current foundation:

- native macOS PyInstaller build on GitHub runner;
- tar.gz archive in CI.

Not yet claimed:

- Developer ID signing;
- hardened runtime/entitlements acceptance;
- notarization;
- stapling;
- DMG/PKG production distribution;
- Gatekeeper clean-machine acceptance;
- universal/architecture strategy beyond the actual runner/build being tested.

## Linux distribution status

Current foundation:

- Ubuntu-hosted PyInstaller build;
- tar.gz archive.

Not yet claimed:

- AppImage;
- `.deb`/`.rpm`;
- repository/package signing;
- broad distro/glibc compatibility;
- Flatpak/Snap.

Do not state those formats are available until corresponding build/release code and acceptance exist.

## Build Smoke is not Package Desktop

`Build Smoke` runs on every relevant development event and verifies:

- source compilation;
- CLI entry point;
- accessibility smoke;
- packaging preflight.

It does **not** invoke a complete production package/signing process.

`Package Desktop` actually invokes PyInstaller, but its archives remain unsigned development artifacts.

## Signing credentials

Production signing secrets must never be committed to the repository.

Use protected CI secret stores/HSM/certificate services and platform-appropriate least-privilege controls.

Document:

- certificate identity;
- expiration/renewal procedure;
- timestamping/notarization endpoint requirements;
- secret rotation;
- who can trigger signing;
- verification commands;
- incident response for compromised credentials.

## Artifact hashing

Every distributed artifact should have a SHA-256 recorded after the final signing/archive step that users download.

Hashing an unsigned intermediate is not sufficient if signing later changes the binary bytes.

Release records should include:

```text
filename
byte size
SHA-256
commit/tag
workflow run ID
platform/architecture
signing/notarization status
```

## Packaged-app smoke testing

Before release, test the package itself—not only source Python.

Minimum representative packaged-app test:

- launch UI;
- open/create project;
- source selection/file dialogs;
- dry-run/preflight;
- PDF merge;
- DOCX merge;
- mixed project merge;
- generated evidence;
- encrypted PDF prompt;
- cancellation;
- recovery path;
- Unicode/long paths;
- branding resources;
- application exit/relaunch.

Perform on clean machines/VMs representative of target users.

## One-file versus onedir

Treat these as separate distribution targets.

One-file builds can extract bundled files to temporary runtime locations and can differ in startup time, antivirus behavior, resource-path semantics, and crash cleanup.

Do not ship one-file simply because it is convenient without testing its real target behavior.

## Reproducibility

Centralized arguments improve reproducibility, but bit-for-bit reproducible binaries are not currently claimed.

For a release, pin/record as much build context as practical:

- OS runner image;
- Python version;
- dependency versions;
- PyInstaller version;
- commit/tag;
- workflow run;
- final hash.

## Release tag behavior

Package Desktop triggers for tags matching:

```text
v*
```

Before pushing a release tag:

- ensure it points to the final reviewed commit;
- ensure changelog/version are correct;
- ensure source CI is green;
- ensure unresolved release blockers are documented;
- understand that the resulting CI artifacts are still unsigned unless a future signing stage is explicitly added.

## Production packaging definition of done

A platform packaging target is complete only when:

- package builds consistently;
- packaged app passes functional acceptance on clean machine;
- recovery/fidelity/accessibility paths relevant to that platform are accepted;
- installer/distribution format is intentional;
- signing/notarization succeeds where required;
- final artifact signature is verified independently;
- final download hash is recorded;
- installation/launch/update/uninstall behavior is documented;
- release notes correctly state support/limitations.

Until then, use the phrase **unsigned development build** for the current CI artifacts.
