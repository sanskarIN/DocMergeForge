# Executable Build Troubleshooting

This guide focuses specifically on failures while building or launching packaged DocMergeForge executables.

## Start with a clean reproduction

Before debugging a strange package failure:

1. record OS/Python/PyInstaller versions;
2. confirm the intended commit;
3. run packaging preflight;
4. remove only `build/` and `dist/`;
5. rebuild in a fresh virtual environment if necessary;
6. reproduce outside the repository checkout.

## Packaging preflight fails

Command:

```bash
python scripts/build_desktop.py --check
```

The selected root must contain:

```text
pyproject.toml
src/docmergeforge/ui/main.py
```

Use:

```bash
python scripts/build_desktop.py --check --root /correct/path/to/DocMergeForge
```

Do not bypass root validation by copying individual files into random directories.

## `PyInstaller is required`

Install the build extra:

```bash
pip install -e ".[build]"
```

Confirm:

```bash
python -m PyInstaller --version
```

## Wrong Python is being used

Check:

```bash
python -c "import sys; print(sys.executable); print(sys.version)"
```

On Windows:

```powershell
Get-Command python
py -0p
```

Recreate the virtual environment with Python 3.12 for packaging parity.

## Editable install points to another checkout

Check:

```bash
python -c "import docmergeforge, pathlib; print(pathlib.Path(docmergeforge.__file__).resolve())"
```

If it points to a different checkout, recreate the venv and reinstall from the intended repository.

## Build succeeds but executable does not launch

Launch from a terminal when possible to capture errors.

Check for:

- missing DLL/shared library;
- missing Qt plugin;
- missing bundled package/submodule;
- resource path failure;
- unsupported OS/runtime;
- permissions;
- one-file extraction failure;
- endpoint protection quarantine.

Fix shared build configuration in `src/docmergeforge/packaging/desktop.py` when the issue affects packaging generally.

## Qt platform plugin errors

Symptoms can mention inability to initialize a Qt platform plugin.

Actions:

- confirm PySide6 installed in the build environment;
- inspect PyInstaller output for Qt collection warnings;
- inspect packaged Qt plugin directories;
- test with a clean build;
- on Linux, verify graphical runtime libraries/display session;
- compare behavior with Build Smoke.

Do not require users to copy arbitrary Qt DLLs from a developer machine as a release solution.

## Linux `libEGL.so.1` error

On Ubuntu/Debian, install the runtime used by repository CI:

```bash
sudo apt-get update
sudo apt-get install -y libegl1
```

Other distributions need equivalent packages.

## App runs only from repository directory

This usually indicates an accidental resource/current-working-directory dependency.

Test from another directory and inspect resource loading.

The packaged app should locate bundled resources independently of the checkout.

## Branding/assets are missing

The shared packaging configuration includes `assets/branding` only when the directory exists.

Verify:

```text
assets/branding/
```

exists before build.

Then inspect the packaged output and the application resource-loading code.

If asset paths change, update build configuration and tests/documentation together.

## `docxcompose`, `docx`, or `pypdf` functionality missing

The build helper currently uses `--collect-all` for these packages.

If a future dependency still fails in the packaged app:

- reproduce with a minimal packaged workflow;
- inspect PyInstaller analysis/warnings;
- determine required hidden imports/data/binaries;
- add the fix centrally to packaging configuration;
- add a packaging regression test where practical.

## `docmergeforge` submodule missing

The helper uses:

```text
--collect-submodules docmergeforge
```

If a dynamically imported module is still missed, inspect the import path and PyInstaller analysis rather than duplicating the entire source tree into `dist` manually.

## One-file works differently from onedir

Expected causes include:

- temporary extraction path;
- startup timing;
- resource lookup;
- antivirus scanning;
- temporary filesystem permissions;
- executable mount restrictions.

Use onedir as the baseline and test onefile separately.

## One-file fails because temp directory is restricted/full

One-file applications extract runtime content during launch.

Check OS temp directory space/permissions and security policy. If this is a target-environment limitation, onedir may be the more appropriate distribution mode.

Do not silently switch production mode without documenting/testing it.

## Windows SmartScreen warning

Unsigned/new artifacts may trigger Windows trust warnings.

Actions:

- verify artifact hash/source;
- sign production artifacts using an appropriate code-signing identity;
- verify Authenticode status;
- do not instruct users to disable Defender/SmartScreen permanently.

## Windows antivirus quarantines the file

One-file packagers can attract heuristic false positives.

Actions:

- verify the build machine/source is clean;
- compare onedir vs onefile;
- use reputable signing for production;
- submit false-positive reports to the security vendor when appropriate;
- retain artifact hashes;
- do not disable security software as the standard fix.

## macOS says app is damaged/unidentified developer

Possible causes:

- unsigned application;
- invalid/broken signature;
- quarantine/Gatekeeper behavior;
- bundle mutation after signing;
- failed/missing notarization.

Inspect:

```bash
codesign -dv --verbose=4 <app>
codesign --verify --deep --strict --verbose=2 <app>
spctl --assess --type execute --verbose=4 <app>
```

Do not present Gatekeeper bypass commands as the normal production installation path.

## macOS notarization rejected

Inspect the notarization result/log, correct the underlying issue, rebuild/resign if bytes change, and resubmit.

Do not ship while calling the artifact notarized.

## Linux app works on build host but not older distro

Likely causes include glibc/runtime compatibility.

Record build baseline:

```bash
ldd --version | head -n 1
```

Build on an appropriately old compatible baseline or choose another packaging strategy. Do not assume forward-built binaries run on older systems.

## Linux executable permission lost after extraction

Inspect:

```bash
ls -l <executable>
```

If archive creation did not preserve executable bits, fix the packaging/archive process. Manual `chmod +x` is useful for diagnosis but should not be required in a polished release archive.

## File dialogs fail in packaged app

Check platform Qt integration/plugins and run in a real graphical session.

Test both native source app and packaged app to isolate packaging-only behavior.

## Merge works from CLI but not packaged GUI

Check:

- bundled dependencies;
- GUI worker/import paths;
- resource/config path assumptions;
- permissions/output directory;
- packaged diagnostics/logs;
- the exact error surfaced by the GUI.

Create a minimal project fixture to reproduce consistently.

## Output folder permission error

This is an application/runtime issue rather than a packaging build failure.

Choose a user-writable output folder. The application performs a write probe before expensive project work.

Do not run the entire app as administrator/root merely to bypass a normal permissions problem.

## Executable is unexpectedly huge

PyInstaller bundles Python, Qt, and dependencies, so desktop artifacts can be large.

Before attempting size optimization:

- inspect actual contents;
- identify duplicate/unneeded packages;
- avoid removing modules blindly;
- preserve required Qt/document libraries;
- rerun full packaged-app acceptance after any exclusion.

Correctness is higher priority than unverified size reduction.

## Rebuild appears to use stale content

Clean:

Windows:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
```

macOS/Linux:

```bash
rm -rf build dist
```

The helper already passes `--clean`, but deleting generated output can simplify diagnosis.

Also verify the editable install points to the current checkout.

## CI succeeds locally but Package Desktop fails

Compare:

- OS image;
- Python version;
- dependency versions;
- environment variables;
- path casing;
- shell syntax;
- generated `dist` layout.

Inspect the exact failing workflow step: install, preflight, build, archive, or upload.

## Package Desktop builds but archive step fails

Inspect actual `dist` output. The workflow currently assumes:

```text
dist/DocMergeForge
```

If PyInstaller output differs on a platform/version, update the archive command and documentation based on observed output.

## Signature invalid after packaging change

Any modification to signed bytes can invalidate a signature.

Sign after final executable/bundle assembly, and regenerate final hashes after signing/notarization/container creation.

## Hash does not match published value

Do not launch/distribute until resolved.

Check:

- correct artifact version;
- whether signing/notarization changed bytes after hash generation;
- archive was regenerated;
- download corruption;
- wrong file selected.

Publish corrected hashes only after re-verification.

## Last-resort diagnostic bundle

For a reproducible support report include:

```text
Commit/tag
OS/version/architecture
Python version
PyInstaller version
Build mode
Exact build command
Packaging preflight output
Relevant PyInstaller error/warning
Launch error
Artifact hash
Whether issue reproduces outside repository
Whether clean machine reproduces
```

Do not include private manuscripts, passwords, signing secrets, or private keys.
