# Executable Verification Guide

A successful build command is only the beginning. This guide defines how to verify a DocMergeForge executable before distribution.

## Verification levels

### Level 1 — Build-host verification

Confirms PyInstaller produced output and the packaged application can initialize/execute its smoke workload on the same machine that built it.

### Level 2 — Downloaded-artifact fresh-runner verification

Confirms the uploaded archive can be downloaded on a separate runner that has no repository checkout or installed DocMergeForge/Python build environment, its SHA-256 sidecar matches, it extracts correctly, and its packaged application executes the real mixed PDF+DOCX smoke workload.

The current Linux fresh-runner job installs only the system `libegl1` runtime required by packaged PySide6/Qt.

### Level 3 — Human clean-machine interactive verification

Confirms the artifact behaves correctly on representative end-user machines/VMs without the development environment, including interactive dialogs, platform trust prompts, encrypted-PDF entry, cancellation, accessibility, and representative manuscripts.

### Level 4 — Production trust/distribution verification

Confirms final hashes, signatures/notarization where claimed, installer/package behavior, update/uninstall behavior, and target-platform acceptance.

A production release should not stop at Level 1 or Level 2.

## Current automated executable evidence

### Default onedir

Package Desktop run `32024177298` at checkpoint `a325c12e89e0bc6dc9798f80fb866f469165647f` completed successfully on Windows, macOS, and Ubuntu.

For every platform it completed:

1. native PyInstaller build;
2. build-host packaged mixed PDF+DOCX smoke;
3. archive creation;
4. archive SHA-256 sidecar creation/verification;
5. artifact upload;
6. separate fresh-runner artifact download;
7. checksum verification on the downloaded archive;
8. extraction;
9. execution of `--packaged-smoke` again without source checkout/project installation.

### Onefile

Onefile Acceptance run `32024284609` at checkpoint `6720e7a8a8cbbcad79c7e0c9c853c2382ae4a277` completed successfully on Windows, macOS, and Ubuntu.

It performs the same build-host plus downloaded-artifact/fresh-runner acceptance for `scripts/build_desktop.py --one-file`.

This evidence means both repository-supported PyInstaller modes now have automated Level 1 and Level 2 acceptance on all three desktop CI runner families.

It does **not** convert Level 3 human interactive acceptance or Level 4 signing/notarization into completed claims.

## 1. Capture build identity

Record:

```text
Repository commit/tag:
Build OS:
Architecture:
Python version:
PyInstaller version:
Build mode: onedir/onefile
Build command:
CI workflow/run ID:
Artifact label:
Artifact SHA-256:
Fresh-runner result:
```

The reusable provenance generator can automate much of this metadata; see [Build Provenance](provenance.md).

## 2. Inspect artifact contents

For onedir builds, inspect the package directory rather than assuming all resources are present. Check the executable/application bundle, Qt/PySide runtime, document-processing dependencies, branding/resources, and obvious accidental private/source inclusions.

For onefile, inspect both the distribution archive and runtime behavior because embedded contents are extracted internally at execution time.

## 3. Verify the exact downloaded archive

Do not test only the pre-upload `dist` directory when evaluating a distributable artifact.

For automated CI, Package Desktop and Onefile Acceptance now:

- upload the archive + `.sha256` sidecar;
- start a new runner;
- download the named artifact;
- recompute/verify SHA-256;
- extract the archive;
- locate the packaged executable/bundle;
- execute packaged smoke.

This detects upload/archive/layout/permission corruption that a build-host-only launch cannot.

## 4. Launch outside repository

For local/manual acceptance, copy/extract the artifact to a location unrelated to the source checkout and launch it there.

Pass condition: the application does not require repository-relative Python files or an editable installation.

## 5. Automated packaged publication smoke

`--packaged-smoke` is a PyInstaller acceptance interface, not a normal user mode. It currently:

- initializes Qt/application settings/logging/theme offscreen;
- constructs the desktop main window without onboarding/recovery dialogs;
- creates a temporary Part 1 PDF and Part 1 DOCX;
- runs `MergeApplicationService` with expected range 1–1;
- exercises PDF front matter/page numbering and ReportLab;
- exercises DOCX composition;
- exercises source hashing, output locking, transactional publication, reporting, manifest, and checksum generation;
- requires exactly two validated manuscript outputs plus manifest/checksum evidence;
- exits nonzero if the packaged workload fails.

This gives strong small-fixture functional evidence, but does not replace representative manuscript/human UI QA.

## 6. Human basic UI smoke

On a representative clean end-user environment, verify main window/branding, project creation, file/folder selection, order editor, settings, help/support/about, recent projects/recovery UI, and normal application exit/relaunch.

## 7. Representative PDF packaged-app merge

Use a small but realistic numbered PDF fixture and verify discovery, ordering, validation, output selection, publication, output reopen, expected pages, reports/manifest/checksums, bookmarks/front matter/overlays as applicable.

## 8. Representative DOCX packaged-app merge

Use DOCX input with paragraphs, headings, tables, lists/numbering, sections, headers/footers, media, links/fields where appropriate. Verify structural output and human rendering in the intended editor.

Portable structural tests are not proof of universal Microsoft Word fidelity.

## 9. Mixed PDF + DOCX project

Verify independent format validation, one publication transaction, matching evidence, and no partial newer format if the other fails before publication.

The automated packaged smoke already covers a minimal mixed project; human acceptance should use representative content.

## 10. Encrypted PDF

Using a PDF you are authorized to open, verify password prompt, incorrect-password rejection, successful correct-password merge, and absence of persisted password in project/report/provenance output.

## 11. Cancellation and recovery

Verify interactive cancellation behavior in packaged UI and, when relevant, the recovery command/workflow. Cross-platform source-level Recovery Acceptance separately proves deterministic journal rollback after real forced `os._exit()` at multiple promotion phases.

See [Publication Recovery](../recovery.md).

## 12. Filesystem/path tests

Verify spaces, Unicode, long valid paths, non-writable destinations, low-space behavior appropriate to the platform, and removable/network storage only if claimed.

Linux has real tmpfs `ENOSPC` acceptance; additional filesystem/platform claims remain separate.

## 13. Resource/current-directory test

Launch from a different current working directory and verify bundled branding/resources still load. Fresh-runner downloaded-artifact execution already reduces repository-relative dependency risk; manual user-directory testing remains useful.

## 14. Onefile-specific acceptance

Onefile Acceptance now automatically covers native build, real packaged publication smoke, archive/hash, and fresh-runner execution on Windows/macOS/Ubuntu.

Human onefile acceptance should additionally review startup latency, repeated launches, temporary extraction policy/cleanup, restrictive temp storage, endpoint protection reaction, low temp-space behavior, and user-visible crash recovery.

## 15. Human clean-machine acceptance

Use a machine/VM without repository checkout, `.venv`, editable install, or developer Python packages.

Fresh-runner CI is strong automated Level 2 evidence but is intentionally headless/offscreen and does not substitute for this interactive Level 3 gate.

Perform representative PDF/DOCX/mixed workflows, encrypted-PDF interaction, cancellation, accessibility, platform trust behavior, and file-dialog/path scenarios.

## 16. Platform trust checks

### Windows

If signed:

```powershell
Get-AuthenticodeSignature <file> | Format-List
```

With SignTool where available:

```text
signtool verify /pa /v <file>
```

### macOS

If signed/notarized:

```bash
codesign --verify --deep --strict --verbose=2 <app>
spctl --assess --type execute --verbose=4 <app>
```

Verify notarization/stapling where claimed.

### Linux

Verify the exact archive hash and compatibility on every claimed distribution/glibc baseline.

## 17. Final artifact hash

Generate hashes after the final byte-changing operation. Current CI produces hashes for **unsigned** archives. If signing/notarization/repacking changes bytes, generate new final distribution hashes.

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

## 18. Security/privacy inspection

Verify the artifact/archive/provenance does not contain manuscripts, passwords/tokens, signing key material, private diagnostics, or unrelated sensitive local paths.

## 19. Version/provenance

Confirm packaged version/source identity corresponds to the intended release revision. Preserve build provenance and exact archive checksum together.

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

Build-host packaged smoke: PASS/FAIL
Fresh-runner checksum/extract/smoke: PASS/FAIL
Human clean-machine interactive launch: PASS/FAIL/PENDING
Representative PDF merge: PASS/FAIL
Representative DOCX merge: PASS/FAIL
Representative mixed-format project: PASS/FAIL
Encrypted PDF flow: PASS/FAIL/N/A
Cancellation: PASS/FAIL
Recovery: PASS/FAIL
Unicode/space paths: PASS/FAIL
Resource loading: PASS/FAIL
Accessibility manual checks: PASS/FAIL/PARTIAL
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
