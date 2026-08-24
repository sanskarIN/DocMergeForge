# Release Process

This document defines the evidence required to move DocMergeForge from a development checkpoint to a release candidate and, eventually, an intentionally production-accepted release.

A release is not complete merely because source tests pass, a version number changes, or PyInstaller creates an archive.

## Release evidence levels

Keep these states separate:

1. **Implemented** — code exists in the repository.
2. **Automatically verified** — source/integration/acceptance CI is green for the exact behavior being claimed.
3. **Downloaded-artifact verified** — an uploaded executable archive is consumed on a separate native runner without repository checkout or DocMergeForge/Python project installation; signed build/SBOM attestations plus local checksum/provenance are verified against the downloaded archive; the archive is extracted; and packaged smoke succeeds.
4. **Human/production accepted** — representative end-user machines, interactive UX, real manuscript fidelity, accessibility, signing/notarization, installer/distribution behavior, and support expectations meet the intended release claim.

Documentation, changelogs, and releases must not collapse these levels into a single “done” statement.

## Versioning

The current release-preparation target is `2.8.5`. DocMergeForge uses semantic-version-shaped package identifiers, but the repository's evidence model remains authoritative for readiness: a major version greater than zero or one does **not** by itself mean that human/production acceptance, signing/notarization, native mobile packaging, external-office fidelity, or claimed-scale stress gates have passed.

The distribution classifier and release documentation must remain conservative until the corresponding evidence is accepted. For `2.8.5`, treat package/runtime metadata as a candidate identifier first; promote/tag/publish only after the intended release gates for that distribution claim are green and reviewed.

## 1. Freeze release scope

Define the target version, intended changes, supported OS/architectures, supported PyInstaller modes, actual distribution formats, workload/fidelity claims, and known limitations. Stop unrelated feature work during the candidate cycle.

## 2. Update version and documentation

Review/update as appropriate:

```text
pyproject.toml
src/docmergeforge/__init__.py
tests/unit/test_version_metadata.py
CHANGELOG.md
README.md
docs/
PROJECT_STATE.md
what_changed.md
```

Every documented command and support claim must match the candidate implementation. Package metadata and runtime `__version__` must agree, and the release candidate should have an explicit regression pin so accidental version drift fails before publication.

## 3. Source quality and documentation gate

For the exact candidate commit require:

```bash
pre-commit validate-config
ruff check .
black --check --diff .
mypy src/docmergeforge
python scripts/check_docs_links.py
python scripts/check_repository_reference.py
pytest --cov=docmergeforge --cov-report=term-missing
```

Quality must be green on the supported Python matrix. Any source change after that evidence requires a new candidate run.

## 4. 120-part regression gate

Require generated SQL Parts 1–120 fixture creation, regression/integration tests, and CLI Parts 1–120 validation.

This proves the configured numbered-part regression scenario. It does not by itself prove multi-gigabyte performance or advanced real-world fidelity.

## 5. Cross-platform Build Smoke gate

Require Build Smoke on Ubuntu, Windows, and macOS for source compilation, CLI entry point, accessibility metadata/preference smoke, and packaging preflight.

Current automated accessibility preference smoke covers theme application, text-scale bounds/round-trip, and reduced-motion setting round-trip. Human screen-reader/high-contrast/layout acceptance remains separate.

## 6. Security gate

Require CodeQL/security checks appropriate to the candidate. Review dependency changes/advisories and ensure no credentials/private manuscripts enter repository fixtures, logs, provenance, SBOMs, telemetry, or release artifacts.

## 7. Recovery and locking gate

Require transactional publication, rollback, cancellation, recovery, fingerprint fail-closed behavior, and cross-process output-lock tests.

When recovery semantics change, require Recovery Acceptance. Current controlled evidence includes real `os._exit()` interruption after the first rollback backup, after the first final promotion, and after the last final promotion before journal commit on Windows/macOS/Ubuntu.

Controlled process termination does not replace power-loss, device-removal, filesystem-corruption, or multi-host network-lock testing when those environments are claimed.

## 8. Disk/storage gate

Require storage/writeability tests and disk-exhaustion evidence appropriate to the support statement.

Current real filesystem-exhaustion evidence is Linux tmpfs `ENOSPC`; NTFS/APFS/removable/network filesystems require their own acceptance if specifically claimed.

## 9. Stress/resource gate

Use Stress Acceptance at parameters whose **measured generated source byte total** reaches the workload class being claimed. Record exact fixture parameters, source/output bytes, validation/compare results, workflow run, and resource telemetry where relevant.

Current automated default 120-part telemetry is recorded in [Release Evidence Ledger](release-evidence.md) and [Stress Testing](stress-testing.md). It uses approximately 9.9 MB of generated source data and therefore is **not** multi-gigabyte acceptance.

Never describe a run as multi-gigabyte unless measured source bytes actually reach that class.

## 10. Real-world fidelity gate

Use a privacy-safe representative corpus and human review in the intended PDF/office applications. Portable DOCX mode remains the production path until external Word/LibreOffice adapters have independent implementation and acceptance evidence.

## 11. Accessibility gate

Automated accessibility metadata/preference smoke is supporting evidence. Human acceptance should cover keyboard-only operation, intended screen readers, real high-contrast/theme behavior, text/display scaling, reduced motion, large lists/error states, localization/readability, and representative platform workflows.

## 12. Default onedir package gate

For distributed onedir builds, require Package Desktop on Windows/macOS/Ubuntu.

The current verified workflow sequence includes native PyInstaller build, packaged mixed PDF+DOCX smoke, archive creation, SHA-256 sidecar, privacy-safe archive-bound JSON provenance, CycloneDX 1.6 build-environment dependency SBOM, signed GitHub/Sigstore build-provenance attestation, signed CycloneDX SBOM predicate, artifact upload, fresh-runner download, independent verification of both signed predicates, provenance/checksum verification, extraction, and packaged mixed-document smoke again.

Current verified CycloneDX evidence:

```text
Run:        32033135355
Checkpoint: 59dc14bbf1d4301177e475ac350694bdd9d90ada
```

All Windows/macOS/Ubuntu build-host and fresh-runner jobs passed for that historical checkpoint. Re-run/review candidate-appropriate packaging evidence before attributing it to `2.8.5`.

## 13. Optional onefile gate

If `--one-file` is supported or distributed, test it independently from onedir using the same archive/checksum/provenance/SBOM/two-attestation/fresh-runner sequence.

Current verified CycloneDX evidence:

```text
Run:        32033541414
Checkpoint: dc624e23d07e0ce94ef345245630d153ee60091a
```

All Windows/macOS/Ubuntu build-host and fresh-runner jobs passed for that historical checkpoint. Do not relabel it as `2.8.5` evidence unless the exact candidate commit is the checkpoint being verified.

## 14. Build provenance and SBOM gate

Retain all four current unsigned-build evidence layers:

- exact archive `.sha256` sidecar;
- privacy-safe DocMergeForge JSON provenance bound to archive filename/size/SHA-256;
- signed GitHub/Sigstore build-provenance attestation;
- CycloneDX 1.6 build-environment dependency SBOM plus signed `https://cyclonedx.org/bom` predicate.

Fresh runners must verify both signed predicates independently, then verify local archive-bound provenance and checksum before execution.

The CycloneDX document describes the Python build environment used by PyInstaller and may include build-time dependencies; do not call it a byte-perfect post-bundling binary inventory.

See [Build Provenance](build/provenance.md) and [Release Evidence Ledger](release-evidence.md).

## 15. Human interactive clean-machine gate

Downloaded-artifact fresh-runner CI is strong automated Level-2 evidence, but it is headless/offscreen and deterministic.

Before a production support claim, use representative clean end-user machines/VMs to test normal UI launch, file dialogs/source selection, ordering, encrypted-PDF entry, cancellation/recovery UX, Unicode/long paths, accessibility, platform trust prompts, representative PDF/DOCX/mixed projects, and normal exit/relaunch.

## 16. Platform signing/notarization gate

Current artifacts are explicitly unsigned development builds unless final-stage evidence says otherwise.

### Windows

When production signing is claimed, sign the intended executable/installer with protected credentials and timestamp it. Verify Authenticode independently and review SmartScreen/trust behavior on a clean machine.

### macOS

When production distribution is claimed, complete Developer ID signing, hardened-runtime/entitlements review where required, notarization, stapling, and Gatekeeper verification on a clean Mac.

### Linux

Define the actual distribution/package trust mechanism and compatibility baseline for the formats/distributions being claimed.

Never commit production signing credentials.

## 17. Final artifact hashes/provenance/SBOM

Current CI sidecars, local provenance, CycloneDX SBOMs, and GitHub attestations describe exact **unsigned** archives at their build stage.

For a production release, generate SHA-256 and appropriate final-stage provenance/SBOM/attestations after the last byte-changing signing/notarization/repackaging operation. Do not reuse unsigned archive evidence for changed signed bytes.

## 18. Installer/distribution acceptance

If distributing MSI/MSIX/Inno/NSIS/DMG/PKG/AppImage/DEB/RPM/etc., test the actual installer/container separately: installation/extraction, launch, upgrade, uninstall, user-data preservation, permissions, shortcuts/associations where relevant, trust/signature behavior, and cleanup.

## 19. Final documentation/release-note review

Review installation, getting started, CLI/desktop guides, recovery, executable building/verification/provenance, known limitations, privacy/security, accessibility, stress evidence, changelog, support/contact information, and release notes.

Release notes should state supported platforms/architectures/build modes, workload/fidelity/accessibility limitations, signing/notarization status, artifact hashes, provenance/SBOM evidence, and recovery/upgrade guidance accurately.

## 20. Tag and publish only after acceptance

A `v*` tag can trigger packaging, but the tag itself is not acceptance and does not make current artifacts signed.

Tag only the chosen reviewed commit after required gates for the release claim are green/accepted. For the current cycle, do not create or describe `v2.8.5` as accepted merely because package metadata says `2.8.5`.

## 21. Post-release verification

After publishing through the real user-facing channel:

1. download the released artifacts as users would;
2. verify final hashes, signed provenance/SBOM predicates, signatures/notarization as applicable;
3. install/extract and launch on representative targets;
4. perform a small publication smoke;
5. verify release notes/docs/support links;
6. confirm no private/debug files were uploaded;
7. retain run IDs, provenance/SBOM/checksums, trust evidence, and human acceptance records.

## Production-acceptance gate

Do not claim a production-accepted release until required areas for the intended support statement are intentionally accepted, including core merge correctness, transaction/recovery safety, representative large/stress workloads, real-world fidelity, human accessibility, downloaded-artifact and human clean-machine package acceptance, production signing/notarization where distributed, and complete documentation/support/security processes.

This gate applies to `2.8.5` regardless of its numeric major version.

## Release evidence template

```text
Version/tag:
Commit SHA:
Date:
Quality run:
Project Sync Safety run:
120-Part Regression run:
Build Smoke run:
Security run:
Recovery Acceptance run:
Disk Full Acceptance run:
Stress run(s):
Package Desktop run:
Onefile Acceptance run (if distributed):
Windows fresh-runner verification:
macOS fresh-runner verification:
Linux fresh-runner verification:
Archive SHA-256 values:
DocMergeForge provenance files:
CycloneDX SBOM files:
Build-provenance attestation verification:
CycloneDX predicate verification:
Human clean-machine acceptance records:
Fidelity corpus result:
Accessibility acceptance record:
Windows signature verification:
macOS notarization verification:
Linux distribution verification:
Known limitations:
Release approver/notes:
```

See also [Executable Verification](build/verification.md), [Build Provenance](build/provenance.md), [Release Build Checklist](build/release-checklist.md), [Release Evidence Ledger](release-evidence.md), [Known Limitations](known-limitations.md), [Testing and CI](testing-and-ci.md), and [Stress Testing](stress-testing.md).
