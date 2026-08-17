# Release Process

This document defines the evidence required to move DocMergeForge from a development checkpoint to a release candidate and, eventually, a stable `v1.0.0` release.

A release is not complete merely because source tests pass or PyInstaller creates an archive.

## Release evidence levels

Keep these states separate:

1. **Implemented** — code exists in the repository.
2. **Automatically verified** — source/integration/acceptance CI is green for the exact behavior being claimed.
3. **Downloaded-artifact verified** — an uploaded executable archive is consumed on a separate native runner without repository checkout or DocMergeForge/Python project installation; checksum/provenance are verified against the exact archive bytes; the archive is extracted; and the packaged application executes successfully.
4. **Human/production accepted** — representative end-user machines, interactive UX, real manuscript fidelity, accessibility, signing/notarization, installer/distribution behavior, and support expectations meet the intended release claim.

Documentation, changelogs, and releases must not collapse these levels into a single “done” statement.

## Versioning

The project follows semantic-versioning intent. The package remains pre-stable (`0.x`) while the release matrix is being completed. `1.0.0` is reserved for the first intentionally accepted stable public contract.

## 1. Freeze release scope

Define the target version, intended changes, supported OS/architectures, supported PyInstaller modes, actual distribution formats, workload/fidelity claims, and known limitations. Stop unrelated feature work during the candidate cycle.

## 2. Update version and documentation

Review/update as appropriate:

```text
pyproject.toml
CHANGELOG.md
README.md
docs/
what_changed.md
```

Every documented command and support claim must match the candidate implementation.

## 3. Source quality and documentation gate

For the exact candidate commit require:

```bash
ruff check .
black --check --diff .
mypy src/docmergeforge
python scripts/check_docs_links.py
pytest --cov=docmergeforge --cov-report=term-missing
```

Quality must be green on the supported Python matrix. Any source change after that evidence requires a new candidate run.

## 4. 120-part regression gate

Require generated SQL Parts 1–120 fixture creation, regression/integration tests, and CLI Parts 1–120 validation.

This proves the configured numbered-part regression scenario. It does not by itself prove multi-gigabyte performance or advanced real-world fidelity.

## 5. Cross-platform Build Smoke gate

Require Build Smoke on Ubuntu, Windows, and macOS for source compilation, CLI entry point, accessibility metadata smoke, and packaging preflight.

## 6. Security gate

Require CodeQL/security checks appropriate to the candidate. Review dependency changes/advisories and ensure no credentials/private manuscripts enter repository fixtures, logs, provenance, or release artifacts.

## 7. Recovery and locking gate

Require transactional publication, rollback, cancellation, recovery, fingerprint fail-closed behavior, and cross-process output-lock tests.

When recovery semantics change, require the dedicated Recovery Acceptance workflow. Current controlled evidence includes real `os._exit()` interruption after the first rollback backup, after the first final promotion, and after the last final promotion before journal commit on Windows/macOS/Ubuntu.

Controlled process termination does not replace power-loss, device-removal, filesystem-corruption, or multi-host network-lock testing when those environments are claimed.

## 8. Disk/storage gate

Require storage/writeability tests and disk-exhaustion evidence appropriate to the support statement.

Current real filesystem-exhaustion evidence is Linux tmpfs `ENOSPC`; NTFS/APFS/removable/network filesystems require their own acceptance if specifically claimed.

## 9. Stress/resource gate

Run the manual Stress Acceptance workflow at parameters whose **measured generated source byte total** reaches the workload class being claimed. Record fixture parameters, measured source/output sizes, validation/compare results, workflow run ID, and resource observations.

Never describe a run as multi-gigabyte unless the generated source data actually reaches that class.

## 10. Real-world fidelity gate

Use a privacy-safe representative corpus and human review in the intended PDF/office applications. Portable DOCX mode remains the production path until external Word/LibreOffice adapters have independent implementation and acceptance evidence.

## 11. Accessibility gate

Automated accessibility smoke is supporting evidence. Human acceptance should cover keyboard-only operation, intended screen readers, high contrast/theme behavior, text/display scaling, reduced motion, large lists/error states, and representative platform workflows.

## 12. Default onedir package gate

For distributed onedir builds, require `Package Desktop` on Windows/macOS/Ubuntu.

The workflow must complete:

- native PyInstaller build;
- build-host packaged mixed PDF+DOCX smoke;
- archive creation;
- archive SHA-256 sidecar generation;
- privacy-safe provenance bound to archive filename/size/SHA-256;
- artifact upload;
- separate fresh-runner download without repository checkout/project installation;
- provenance validation for source SHA, build mode, artifact label, trust state, archive filename, byte size, and SHA-256;
- independent checksum-sidecar validation;
- extraction;
- packaged mixed PDF+DOCX smoke again.

**Verified evidence:** Package Desktop run `32025126032`, checkpoint `59107192d494d76a4112cdeaa9a55f01cfe37972`, passed the complete build-host and fresh-runner sequence on Windows, macOS, and Ubuntu.

## 13. Optional onefile gate

If `--one-file` is supported or distributed, test it independently from onedir.

`Onefile Acceptance` must complete the same native build, packaged publication smoke, archive/checksum/provenance upload, and fresh-runner archive-bound verification sequence.

**Verified evidence:** Onefile Acceptance run `32025167433`, checkpoint `b8a181b7138a1bc617766dd3e86c9ab32aade75e`, passed all build-host and fresh-runner jobs on Windows, macOS, and Ubuntu.

## 14. Build provenance gate

Use `scripts/write_build_provenance.py` / `docmergeforge.packaging.provenance` to retain privacy-safe artifact identity.

The current schema records application/version, artifact label/build mode, explicit unsigned/not-notarized state, source commit/repository/ref, OS/architecture, Python/PyInstaller versions, allowlisted CI identity, installed distribution versions, and—when an archive is supplied—its exact filename, byte size, and SHA-256.

The generator deliberately excludes arbitrary environment variables, secrets, manuscript paths, and document contents.

Fresh-runner validation must require provenance archive identity to match the downloaded archive in addition to independently verifying the `.sha256` sidecar.

See [Build Provenance](build/provenance.md).

## 15. Human interactive clean-machine gate

Downloaded-artifact fresh-runner CI is strong automated Level-2 evidence, but it is headless/offscreen and deterministic.

Before a production support claim, use representative clean end-user machines/VMs to test normal UI launch, file dialogs/source selection, ordering, encrypted-PDF entry, cancellation/recovery UX, Unicode/long paths, accessibility, platform trust prompts, representative PDF/DOCX/mixed projects, and normal exit/relaunch.

## 16. Platform signing/notarization gate

Current artifacts are explicitly unsigned development builds.

### Windows

When production signing is claimed, sign the intended executable/installer with protected credentials and timestamp it. Verify Authenticode independently and review SmartScreen/trust behavior on a clean machine.

### macOS

When production distribution is claimed, complete Developer ID signing, hardened-runtime/entitlements review where required, notarization, stapling, and Gatekeeper verification on a clean Mac.

### Linux

Define the actual distribution/package trust mechanism and compatibility baseline for the formats/distributions being claimed.

Never commit production signing credentials.

## 17. Final artifact hashes/provenance

Current CI sidecars/provenance describe exact **unsigned** archives.

For a production release, generate SHA-256 and appropriate final-stage provenance/attestation after the last byte-changing signing/notarization/repackaging operation. Do not reuse unsigned archive evidence for changed signed bytes.

## 18. Installer/distribution acceptance

If distributing MSI/MSIX/Inno/NSIS/DMG/PKG/AppImage/DEB/RPM/etc., test the actual installer/container separately: installation/extraction, launch, upgrade, uninstall, user-data preservation, permissions, shortcuts/associations where relevant, trust/signature behavior, and cleanup.

## 19. Final documentation/release-note review

Review installation, getting started, CLI/desktop guides, recovery, executable building/verification/provenance, known limitations, privacy/security, accessibility, changelog, support/contact information, and release notes.

Release notes should state supported platforms/architectures/build modes, workload/fidelity/accessibility limitations, signing/notarization status, artifact hashes, and recovery/upgrade guidance accurately.

## 20. Tag and publish only after acceptance

A `v*` tag can trigger packaging, but the tag itself is not acceptance and does not make current artifacts signed.

Tag only the chosen reviewed commit after required gates for the release claim are green/accepted.

## 21. Post-release verification

After publishing through the real user-facing channel:

1. download the released artifacts as users would;
2. verify final hashes/provenance/signatures/notarization;
3. install/extract and launch on representative targets;
4. perform a small publication smoke;
5. verify release notes/docs/support links;
6. confirm no private/debug files were uploaded;
7. retain run IDs, provenance, checksums, and human acceptance evidence.

## Stable `v1.0.0` gate

Do not claim `v1.0.0` until required areas for the intended support statement are intentionally accepted, including core merge correctness, transaction/recovery safety, representative large/stress workloads, real-world fidelity, human accessibility, downloaded-artifact and human clean-machine package acceptance, production signing/notarization where distributed, and complete documentation/support/security processes.

## Release evidence template

```text
Version/tag:
Commit SHA:
Date:
Quality run:
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
Build provenance files:
Archive SHA-256 values:
Human clean-machine acceptance records:
Fidelity corpus result:
Accessibility acceptance record:
Windows signature verification:
macOS notarization verification:
Linux distribution verification:
Known limitations:
Release approver/notes:
```

See also [Executable Verification](build/verification.md), [Build Provenance](build/provenance.md), [Release Build Checklist](build/release-checklist.md), [Known Limitations](known-limitations.md), [Testing and CI](testing-and-ci.md), and [Stress Testing](stress-testing.md).
