# Common Executable Build Guide

This guide documents the build steps shared by Windows, macOS, and Linux.

## 1. Start from a known repository revision

For development testing, build from the intended branch or commit. For release work, record the exact commit SHA or tag before building.

Useful commands:

```bash
git status
git rev-parse HEAD
git describe --tags --always --dirty
```

A release build should not be created from an unintentionally dirty working tree. If local changes are intentional, document them and do not present the artifact as matching an unmodified tag.

## 2. Use Python 3.12 for packaging parity

The current Package Desktop workflow uses Python 3.12. A local release-candidate build should use Python 3.12 unless the packaging matrix is deliberately changed and retested.

Check:

```bash
python --version
```

or on Windows:

```powershell
py -3.12 --version
```

## 3. Create an isolated virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Confirm the active interpreter:

```bash
python -c "import sys; print(sys.executable); print(sys.version)"
```

## 4. Install build dependencies

```bash
python -m pip install --upgrade pip
pip install -e ".[build]"
```

The `build` extra currently installs PyInstaller in addition to the normal project dependencies.

For a developer checkout that also needs tests/linting:

```bash
pip install -e ".[dev,build]"
```

If your pip version/environment does not accept combined editable extras as expected, install the two extras separately:

```bash
pip install -e ".[dev]"
pip install -e ".[build]"
```

## 5. Record the environment

For release evidence, record installed versions:

```bash
python -m pip freeze > build-environment.txt
```

This is not a lockfile and does not make the build bit-for-bit reproducible, but it provides useful evidence for diagnosing differences between builds.

Also record:

```bash
python --version
python -m PyInstaller --version
```

## 6. Run source quality checks before packaging

Recommended pre-build checks from the repository root:

```bash
ruff check .
black --check .
mypy src/docmergeforge
pytest
```

For release work, confirm the repository CI results at the same commit rather than relying only on a local run.

## 7. Run packaging preflight

Always run:

```bash
python scripts/build_desktop.py --check
```

The helper validates that the selected repository root contains at least:

```text
pyproject.toml
src/docmergeforge/ui/main.py
```

Expected success form:

```text
Desktop build configuration OK: <resolved-root>
```

### Explicit root

```bash
python scripts/build_desktop.py --check --root /path/to/DocMergeForge
```

If the root is invalid, fix the path rather than bypassing the preflight.

## 8. Understand the current PyInstaller configuration

`src/docmergeforge/packaging/desktop.py` currently generates arguments equivalent in intent to:

```text
<entry-point>
--name DocMergeForge
--windowed
--clean
--noconfirm
--collect-submodules docmergeforge
--collect-all docxcompose
--collect-all docx
--collect-all pypdf
--add-data <assets/branding>:<target>   # when branding exists
--onedir                                 # default
```

The path separator in `--add-data` is generated with `os.pathsep`, so the repository helper uses the correct platform separator.

## 9. Build the recommended onedir application

```bash
python scripts/build_desktop.py
```

Why onedir is the recommended first acceptance target:

- bundled files remain visible for inspection;
- missing shared libraries/resources are easier to diagnose;
- startup avoids one-file extraction overhead;
- antivirus false-positive investigation is usually simpler;
- platform packaging can wrap the directory later.

Generated data is normally placed under:

```text
build/
dist/
```

Do not commit these generated directories unless the repository policy is explicitly changed.

## 10. Build the optional one-file application

```bash
python scripts/build_desktop.py --one-file
```

Treat one-file as a distinct deliverable. It may differ from onedir in:

- startup time;
- temporary extraction behavior;
- runtime resource paths;
- endpoint protection/antivirus behavior;
- crash traces;
- writable/executable temporary-directory requirements.

A successful onedir test does not automatically validate one-file.

## 11. Clean rebuild procedure

When diagnosing packaging state, remove only generated packaging directories.

Windows PowerShell:

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
```

macOS/Linux:

```bash
rm -rf build dist
```

Optionally recreate the virtual environment when dependency contamination is suspected.

Never point cleanup commands at manuscript/output/source directories.

## 12. Launch the actual packaged application

Do not stop at successful PyInstaller exit status. Launch the artifact produced in `dist` on the build OS.

At minimum verify:

- application window opens;
- no Python traceback appears;
- branding/resources render;
- settings/help/about dialogs open;
- file and folder pickers work;
- a small PDF merge completes;
- a small DOCX merge completes;
- output reports are created;
- the application exits normally.

For release acceptance, use the complete [Executable Verification](verification.md) procedure.

## 13. Test from outside the repository

A common packaging mistake is an executable that works only because the source checkout is nearby.

Copy/archive the built artifact to a directory that does not contain the repository and launch it there.

Also verify that the current working directory is not required for resource discovery.

## 14. Test from a clean user profile or machine

For release candidates, test on a clean VM/machine that does not have the project's virtual environment, editable installation, or development dependencies.

This catches:

- missing Qt plugins;
- missing DLLs/shared libraries;
- hidden imports;
- accidental reliance on source files;
- environment-variable dependencies;
- missing runtime system libraries.

## 15. Archive an unsigned development build

### Windows example

```powershell
Compress-Archive -Path dist\DocMergeForge\* -DestinationPath DocMergeForge-Windows-unsigned.zip
```

### macOS/Linux example

```bash
tar -czf DocMergeForge-platform-unsigned.tar.gz -C dist DocMergeForge
```

Use the platform-specific guide because actual macOS output layout may require archiving a `.app` bundle or a containing directory rather than assuming the Linux layout.

## 16. Generate hashes

Windows PowerShell:

```powershell
Get-FileHash .\DocMergeForge-Windows-unsigned.zip -Algorithm SHA256
```

macOS:

```bash
shasum -a 256 DocMergeForge-macOS-unsigned.tar.gz
```

Linux:

```bash
sha256sum DocMergeForge-Linux-unsigned.tar.gz
```

Record hashes with the build commit and test evidence.

## 17. Never confuse executable build with installer build

The repository helper creates a PyInstaller application. It does not currently create these production installer/package formats automatically:

- MSI/MSIX;
- Inno Setup/NSIS installer;
- DMG/PKG;
- AppImage;
- DEB/RPM/Flatpak/Snap.

Those formats can be added later, but each requires its own build recipe, tests, update/uninstall behavior, and release acceptance.

## 18. Build metadata to retain

For every release candidate keep:

- commit SHA/tag;
- OS and architecture;
- Python version;
- PyInstaller version;
- dependency freeze;
- build command/mode;
- CI workflow run ID if applicable;
- artifact filename;
- artifact size;
- SHA-256;
- signing/notarization result if applicable;
- clean-machine verification record.

## 19. What is not currently claimed

The build helper centralizes arguments and CI gives repeatable build infrastructure, but the project does not currently claim:

- bit-for-bit reproducible binaries;
- automatic signed Windows releases;
- automatic macOS notarization;
- universal macOS binaries;
- Linux compatibility across every distro/glibc baseline;
- automatic native installers;
- production readiness solely because PyInstaller completed.

Continue with the native platform guide before distributing an executable.
