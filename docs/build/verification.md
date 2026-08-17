# Executable Verification Guide

A successful build command is only the beginning. This guide defines how to verify a DocMergeForge executable before distribution.

## Verification levels

### Level 1 — Build verification

Confirms PyInstaller produced output and the application starts on the build host.

### Level 2 — Functional packaged-app verification

Confirms the packaged application performs real DocMergeForge workflows without relying on the source checkout.

### Level 3 — Clean-machine verification

Confirms the artifact works on a target machine without the development environment.

### Level 4 — Production trust verification

Confirms final hashes, signatures/notarization where claimed, installer/package behavior, and target-platform acceptance.

A production release should not stop at Level 1.

## 1. Capture build identity

Record:

```text
Repository commit/tag:
Working tree clean/dirty:
Build OS:
Architecture:
Python version:
PyInstaller version:
Build mode: onedir/onefile
Build command:
CI run ID (if applicable):
```

## 2. Inspect artifact contents

For onedir builds, inspect the package directory rather than assuming all resources are present.

Check for:

- executable/application bundle;
- Qt/PySide runtime content;
- Python dependencies;
- branding assets;
- document-processing dependencies;
- obvious accidental source/manuscript inclusions.

Do not distribute test manuscripts, local credentials, or private build files accidentally bundled into `dist`.

## 3. Launch outside repository

Copy/extract the artifact to a location unrelated to the source checkout.

Launch it there.

Pass condition: application does not require repository-relative Python files or the editable installation.

## 4. Basic UI smoke

Verify:

- main window appears;
- application branding renders;
- project creation dialog opens;
- source picker opens;
- order editor opens;
- settings open;
- help/support/about open;
- recent-project UI opens where applicable;
- application closes without crash.

## 5. PDF packaged-app merge test

Prepare a small numbered PDF fixture.

Verify through the packaged desktop application:

1. source discovery;
2. numeric ordering;
3. validation;
4. output-folder selection;
5. merge completion;
6. output PDF exists;
7. output reopens;
8. expected pages are present;
9. report/manifest/checksum evidence is generated when using project workflow.

The packaged executable should be tested, not the source CLI in the same session as a substitute.

## 6. DOCX packaged-app merge test

Prepare a small numbered DOCX fixture containing representative content such as:

- normal paragraphs;
- headings;
- a table;
- basic list/numbering;
- header/footer where practical.

Verify:

- discovery/order;
- validation;
- merge completes;
- DOCX reopens in a compatible editor/parser;
- generated headings/TOC field behavior is as expected;
- reports/manifest are created.

This is structural acceptance, not proof of universal Word fidelity.

## 7. Mixed PDF + DOCX project test

For a project containing both formats:

- verify both format sets validate independently;
- confirm project publication completes as one transaction;
- confirm reports correspond to the published outputs;
- verify no partial newer PDF is left if DOCX fails before promotion.

## 8. Encrypted PDF test

Using a PDF you are authorized to open:

- verify password prompt appears;
- verify an incorrect password is rejected;
- verify the correct password allows the merge;
- verify password is not written into project/report outputs.

Do not use this test to bypass access restrictions.

## 9. Cancellation test

Start a merge large enough to cancel during work.

Verify:

- cancellation is responsive at supported checkpoints;
- final output is not incorrectly reported as successful;
- previous published output remains intact where applicable;
- staging/temporary data is cleaned at safe boundaries.

## 10. Recovery test

For release acceptance, include controlled interrupted-publication testing consistent with the repository recovery documentation.

Verify the packaged application/CLI recovery path can identify journaled interruption evidence and does not destroy conflicting files.

Use [Publication Recovery](../recovery.md) for the operator procedure.

## 11. Filesystem/path tests

Verify at least:

- paths with spaces;
- Unicode filenames/directories;
- long but valid paths;
- non-writable output folder fails safely;
- low-space behavior is handled safely in the planned acceptance environment;
- removable/network filesystems only if those are claimed as supported.

## 12. Resource-path test

Run the app with a different current working directory.

Pass condition: bundled branding/resources still load.

This detects accidental relative-path dependencies.

## 13. One-file extraction acceptance

When distributing `--one-file`, test:

- startup time;
- repeated launches;
- temporary extraction cleanup;
- low-space temporary directory behavior;
- endpoint-protection reaction;
- execution where temp filesystem policies are restrictive;
- resource loading.

One-file should have its own test record.

## 14. Clean-machine acceptance

Test the artifact on a machine/VM without:

- repository checkout;
- `.venv`;
- editable package install;
- developer Python packages.

Perform at least one PDF and one DOCX merge from the packaged desktop application.

## 15. Platform trust checks

### Windows

If signed:

```powershell
Get-AuthenticodeSignature <file> | Format-List
```

And where SignTool is available:

```text
signtool verify /pa /v <file>
```

### macOS

If signed/notarized:

```bash
codesign --verify --deep --strict --verbose=2 <app>
spctl --assess --type execute --verbose=4 <app>
```

Validate notarization/stapling where applicable.

### Linux

Verify archive hash and runtime compatibility on each claimed distro baseline.

## 16. Final artifact hash

Generate hash after final packaging/signing/notarization/container creation.

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

## 17. Archive extraction test

For ZIP/tar.gz distribution:

1. download/copy the final archive;
2. verify SHA-256;
3. extract into a fresh directory;
4. launch the extracted application;
5. perform a small merge.

This catches archive-layout/permission corruption.

## 18. Security/privacy inspection

Before release, verify the artifact/archive does not contain:

- manuscript fixtures not intended for distribution;
- passwords/tokens;
- signing key material;
- local absolute paths in support files where avoidable;
- private diagnostic exports;
- developer-only sensitive files.

## 19. Version/about information

Confirm the packaged app displays the intended application version/release identity where exposed.

Do not publish an artifact under a version label that does not correspond to the built source revision.

## 20. Acceptance record template

```text
DocMergeForge Executable Acceptance
===================================
Commit/tag:
Date:
Platform:
Architecture:
Build mode:
Python:
PyInstaller:
Artifact:
Artifact SHA-256:
CI run:

Launch outside repo: PASS/FAIL
Clean-machine launch: PASS/FAIL
PDF packaged-app merge: PASS/FAIL
DOCX packaged-app merge: PASS/FAIL
Mixed-format project: PASS/FAIL
Encrypted PDF flow: PASS/FAIL/N/A
Cancellation: PASS/FAIL
Recovery: PASS/FAIL
Unicode/space paths: PASS/FAIL
Resource loading: PASS/FAIL
Accessibility smoke/manual checks: PASS/FAIL/PARTIAL
Signature verification: PASS/FAIL/UNSIGNED
Notarization: PASS/FAIL/N/A
Installer/package acceptance: PASS/FAIL/N/A

Known limitations:
Evidence links/run IDs:
Tester:
```

## Release decision

An executable is not production-ready if a required acceptance item fails or remains unverified for a feature/platform being claimed.

Use [Release Build Checklist](release-checklist.md) before publication.
