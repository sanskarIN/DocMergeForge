# Windows Executable Build Guide

This guide covers building, testing, archiving, and preparing DocMergeForge for Windows distribution.

## Scope

The repository currently supports a native Windows PyInstaller build. It does not currently automate MSI/MSIX/Inno Setup/NSIS creation or production code signing.

## Recommended host

Use Windows 11 or a compatible Windows runner with Python 3.12. GitHub Actions currently uses `windows-latest` for Package Desktop.

## 1. Clone and enter the repository

```powershell
git clone https://github.com/sanskarIN/DocMergeForge.git
Set-Location DocMergeForge
```

For release work, checkout the intended tag/commit and record it:

```powershell
git status
git rev-parse HEAD
```

## 2. Create Python 3.12 environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[build]"
```

For full local verification:

```powershell
pip install -e ".[dev]"
```

If PowerShell script execution policy prevents virtual-environment activation, use a permitted shell/environment method for your machine rather than weakening system security globally.

## 3. Verify packaging configuration

```powershell
python scripts/build_desktop.py --check
```

Expected form:

```text
Desktop build configuration OK: C:\...\DocMergeForge
```

## 4. Build onedir

```powershell
python scripts/build_desktop.py
```

The repository's CI archive step currently expects the Windows onedir content below:

```text
dist\DocMergeForge\
```

Inspect this directory before archiving.

## 5. Build one-file when required

```powershell
python scripts/build_desktop.py --one-file
```

Do not replace onedir acceptance with one-file acceptance. Test both independently if both are distributed.

## 6. Launch the packaged application

Find the generated executable under `dist` and launch it from PowerShell and Explorer.

Verify from a normal, non-administrator account when possible.

Minimum checks:

- main window starts;
- no traceback/dialog reports missing Python modules;
- branding loads;
- file/folder pickers open;
- settings/help/about open;
- PDF merge works;
- DOCX merge works;
- reports/manifests/checksums are created for a project run;
- encrypted-PDF prompt works with a legitimate password;
- safe cancellation works;
- application exits cleanly.

## 7. Test Windows path behavior

Exercise:

- spaces in paths;
- Unicode filenames;
- long nested paths that are valid on the target system;
- OneDrive/synced folders if you intend to support them;
- removable/external storage if relevant;
- output folders without elevated privileges.

Do not use only the repository directory for acceptance.

## 8. Clean-machine/VM acceptance

Copy the build to a Windows machine or VM without:

- the DocMergeForge source checkout;
- the development virtual environment;
- Python development packages;
- editable project installation.

Launch and perform a representative merge. This is the strongest practical check for accidental dependency leakage.

## 9. Archive unsigned onedir build

From the repository root:

```powershell
Compress-Archive -Path dist\DocMergeForge\* -DestinationPath DocMergeForge-Windows-unsigned.zip
```

If the destination archive already exists, remove or version it deliberately before rerunning `Compress-Archive`.

The filename must retain `unsigned` until signing has actually been completed and verified.

## 10. Generate SHA-256

```powershell
Get-FileHash .\DocMergeForge-Windows-unsigned.zip -Algorithm SHA256
```

For a single executable:

```powershell
Get-FileHash .\dist\DocMergeForge.exe -Algorithm SHA256
```

Adjust the path to match actual PyInstaller output.

## 11. Inspect Authenticode status

Unsigned development build:

```powershell
Get-AuthenticodeSignature <path-to-executable> | Format-List
```

Do not interpret a built executable as signed unless signature status and signer identity verify successfully.

## 12. Production signing overview

A production Windows distribution normally uses a code-signing certificate and Windows signing tooling. Keep certificates/private keys outside source control.

A typical SignTool shape is:

```text
signtool sign /fd SHA256 /td SHA256 /tr <RFC3161-timestamp-url> <certificate-selection-options> <file>
```

Verification shape:

```text
signtool verify /pa /v <file>
```

Exact certificate selection depends on how the signing identity is provisioned (certificate store, hardware token, managed signing service, etc.). Do not commit PFX passwords or private-key material.

See [Signing and Notarization](signing-and-notarization.md).

## 13. SmartScreen and reputation

Code signing can establish publisher identity, but Windows reputation/SmartScreen behavior is separate and can vary, especially for new applications/certificates.

Acceptance should record:

- whether Windows displays a warning;
- whether publisher information is shown;
- whether the signature verifies;
- whether endpoint protection quarantines or blocks the file.

Never instruct users to disable antivirus as a normal installation requirement.

## 14. Optional installer formats

The repository does not currently ship an installer recipe. If you later add MSI/MSIX/Inno Setup/NSIS, document and test:

- per-user vs per-machine installation;
- install location;
- Start Menu/Desktop shortcuts;
- upgrade behavior;
- downgrade behavior;
- uninstall behavior;
- preservation of user projects/manuscripts;
- file associations, if any;
- repair behavior, if any;
- signed installer and signed payloads;
- clean install on a machine without Python.

Installer creation must be a separate maintained build target rather than an undocumented manual step.

## 15. Windows architecture considerations

Record the architecture of the Python interpreter/build host and target artifact. Do not claim x86, ARM64, or multi-architecture support unless those targets are actually built and tested.

Useful environment checks:

```powershell
python -c "import platform; print(platform.platform()); print(platform.machine())"
```

## 16. DLL/runtime failures

If the app builds but will not launch:

1. launch from PowerShell to capture visible errors;
2. inspect PyInstaller warnings/build output;
3. confirm Qt/PySide6 runtime files are bundled;
4. confirm imported document libraries are present;
5. test from outside the repository;
6. compare with CI Package Desktop behavior;
7. fix shared packaging configuration instead of adding machine-only files manually.

## 17. Windows release evidence

A Windows production candidate should retain:

- commit/tag;
- Windows version/build host;
- architecture;
- Python/PyInstaller versions;
- artifact filename/size/hash;
- Quality/Regression/Build Smoke/Security status;
- clean-machine launch test;
- PDF/DOCX packaged-app merge test;
- cancellation/recovery test;
- signature verification output if signed;
- installer acceptance if an installer is distributed.

## 18. Windows release checklist

- [ ] Build from intended commit/tag.
- [ ] Packaging preflight passes.
- [ ] Clean onedir build completes.
- [ ] Optional one-file build separately passes.
- [ ] Packaged app launches outside repository.
- [ ] Clean-machine launch passes.
- [ ] PDF merge passes.
- [ ] DOCX merge passes.
- [ ] Encrypted-PDF legitimate-password flow passes.
- [ ] Cancellation/recovery passes.
- [ ] Unicode/space path tests pass.
- [ ] Archive hash recorded.
- [ ] Authenticode signature verified before any signed claim.
- [ ] Installer behavior verified if installer is distributed.

Return to the [Build Documentation Portal](README.md) for CI, signing, verification, and troubleshooting guides.
