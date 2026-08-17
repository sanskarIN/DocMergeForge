# Executable Verification Guide

A successful build command is only the beginning. This guide defines how to verify a DocMergeForge executable before distribution.

## Verification levels

### Level 1 — Build-host verification

Confirms PyInstaller produced output and the packaged application can initialize/execute its smoke workload on the same machine that built it.

### Level 2 — Downloaded-artifact fresh-runner verification

Confirms the uploaded archive can be downloaded on a separate native runner with no repository checkout or installed DocMergeForge/Python project environment; signed GitHub build-provenance and CycloneDX SBOM predicates verify; the archive-bound JSON provenance and SHA-256 sidecar match the exact archive bytes; the archive extracts correctly; and its packaged application executes the mixed PDF+DOCX smoke workload.

Linux fresh-runner jobs install only the system `libegl1` runtime required by packaged PySide6/Qt.

### Level 3 — Human clean-machine interactive verification

Confirms the artifact behaves correctly on representative end-user machines/VMs without the development environment, including interactive dialogs, platform trust prompts, encrypted-PDF entry, cancellation, accessibility, and representative manuscripts.

### Level 4 — Production trust/distribution verification

Confirms final post-signing hashes, signatures/notarization where claimed, installer/package behavior, update/uninstall behavior, and target-platform acceptance.

A production release should not stop at Level 1 or Level 2.

## Current automated executable evidence

### Default onedir — verified Level 1 + Level 2

Current CycloneDX acceptance:

```text
Run:        32033135355
Checkpoint: 59dc14bbf1d4301177e475ac350694bdd9d90ada
```

All Windows/macOS/Ubuntu build and fresh-runner jobs passed.

### Onefile — verified Level 1 + Level 2

Current CycloneDX acceptance:

```text
Run:        32033541414
Checkpoint: dc624e23d07e0ce94ef345245630d153ee60091a
```

All Windows/macOS/Ubuntu build and fresh-runner jobs passed.

For every platform/mode the current Level 1 + Level 2 sequence includes:

1. native PyInstaller build;
2. build-host packaged mixed PDF+DOCX smoke;
3. archive creation;
4. archive SHA-256 sidecar creation/verification;
5. archive-bound privacy-safe JSON provenance generation;
6. validated CycloneDX 1.6 build-environment dependency SBOM generation;
7. signed GitHub/Sigstore build-provenance attestation;
8. signed GitHub/Sigstore CycloneDX SBOM attestation;
9. artifact upload including archive/checksum/provenance/SBOM;
10. separate fresh-runner artifact download;
11. default build-provenance attestation verification;
12. explicit `https://cyclonedx.org/bom` predicate verification;
13. provenance validation for source SHA, build mode, artifact label, unsigned/notarized state, archive filename, byte size, and archive SHA-256;
14. independent checksum-sidecar verification;
15. extraction;
16. execution of `--packaged-smoke` again without repository checkout/project installation.

Both repository-supported PyInstaller modes therefore have automated Level 1 and Level 2 acceptance on all three desktop CI runner families.

This does **not** convert Level 3 human interactive acceptance or Level 4 signing/notarization into completed claims. The CycloneDX document describes the Python build environment used by PyInstaller; it is not represented as a byte-perfect post-bundling component inventory.

See [Build Provenance](provenance.md) and [Release Evidence Ledger](../release-evidence.md) for exact artifact IDs/digests and evidence history.

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
Archive byte size:
Archive SHA-256:
Provenance file:
CycloneDX SBOM file:
Build-provenance attestation result:
CycloneDX attestation result:
Fresh-runner result:
```

The provenance/SBOM automation supplies much of this metadata.

## 2. Inspect artifact contents

For onedir builds, inspect the package directory rather than assuming all resources are present. Check the executable/application bundle, Qt/PySide runtime, document-processing dependencies, branding/resources, and obvious accidental private/source inclusions.

For onefile, inspect both the distribution archive and runtime behavior because embedded contents are extracted internally at execution time.

The CycloneDX build-environment SBOM is useful dependency evidence but does not remove the need to inspect actual bundled content when exact binary inventory matters.

## 3. Verify the exact downloaded archive

Do not test only the pre-upload `dist` directory when evaluating a distributable artifact.

Current Package Desktop and Onefile Acceptance fresh-runner jobs:

- download the uploaded archive/checksum/provenance/SBOM artifact;
- verify signed GitHub build provenance for the exact archive;
- separately require the CycloneDX predicate type `https://cyclonedx.org/bom`;
- recompute archive size and SHA-256;
- require provenance archive filename/size/SHA-256 to match;
- require provenance source/mode/label/trust fields to match workflow expectations;
- independently verify the `.sha256` sidecar;
- extract the archive;
- locate the packaged executable/bundle;
- execute packaged smoke.

This detects upload/archive/layout/provenance/attestation/dependency corruption that a build-host-only launch cannot.

Representative commands:

```bash
gh attestation verify <archive> --repo sanskarIN/DocMergeForge

gh attestation verify <archive> \
  --repo sanskarIN/DocMergeForge \
  --predicate-type https://cyclonedx.org/bom
```

## 4. Launch outside repository

For local/manual acceptance, copy/extract the artifact to a location unrelated to the source checkout and launch it there.

Pass condition: the application does not require repository-relative Python files or an editable installation.

## 5. Automated packaged publication smoke

`--packaged-smoke` is a PyInstaller acceptance interface, not a normal user mode. It currently initializes Qt/application settings/logging/theme offscreen; constructs the desktop main window without onboarding/recovery dialogs; creates a temporary Part 1 PDF and Part 1 DOCX; runs `MergeApplicationService` for range 1–1; exercises PDF front matter/page numbering, ReportLab, DOCX composition, source hashing, output locking, transactional publication, reporting, manifest, and checksums; requires exactly two validated manuscript outputs plus manifest/checksum evidence; and exits nonzero if the packaged workload fails.

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

Onefile Acceptance automatically covers native build, real packaged publication smoke, archive/checksum/provenance/SBOM, both signed attestation predicates, and fresh-runner execution on Windows/macOS/Ubuntu.

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

## 17. Final artifact hash and evidence

Generate hashes and final-stage evidence after the last byte-changing operation. Current CI produces hashes, JSON provenance, CycloneDX SBOMs, and GitHub attestations for **unsigned** archives. If signing/notarization/repacking changes bytes, generate new final distribution hashes and appropriate final-stage provenance/attestations.

## 18. Security/privacy inspection

Verify the artifact/archive/provenance/SBOM evidence does not contain manuscripts, passwords/tokens, signing key material, private diagnostics, or unrelated sensitive local paths.

## 19. Version/provenance

Confirm packaged version/source identity corresponds to the intended release revision. Preserve exact archive checksum, local provenance, SBOM, and signed attestation evidence together.

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
Archive SHA-256:
Provenance:
CycloneDX SBOM:
Build-provenance attestation: PASS/FAIL
CycloneDX SBOM attestation: PASS/FAIL
CI run:

Build-host packaged smoke: PASS/FAIL
Fresh-runner provenance/checksum/attestation/extract/smoke: PASS/FAIL
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
