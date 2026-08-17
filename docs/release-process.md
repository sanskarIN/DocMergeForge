# Release Process

This document defines the evidence required to move DocMergeForge from a development checkpoint to a release candidate and, eventually, a stable `v1.0.0` release.

A release is not complete merely because the source tests pass or a PyInstaller archive exists.

## Release philosophy

Keep three states separate:

1. **Implemented** — code exists.
2. **Automatically verified** — CI/test evidence exists for the exact release head.
3. **Production accepted** — real packaged-app, platform, fidelity, accessibility, stress, and signing acceptance has been completed where required.

Documentation, changelogs, and GitHub releases must not collapse those states into one claim.

## Versioning

The project follows semantic versioning intent.

Current package version is pre-stable (`0.x`). Before `1.0.0`, behavior/configuration can still change as release gates are completed.

Typical meaning:

- patch (`0.1.1`) — focused compatible fixes;
- minor (`0.2.0`) — meaningful new capabilities/behavior while pre-stable;
- `1.0.0` — first stable public contract after acceptance matrix is satisfied.

## 1. Freeze release scope

Before creating a release candidate:

- identify target version;
- list intended features/fixes;
- stop unrelated feature additions;
- document known limitations;
- ensure unresolved release blockers are visible;
- decide target operating systems and Python/source support claims;
- decide which package formats will actually be distributed.

## 2. Update version and documentation

Update as appropriate:

```text
pyproject.toml
CHANGELOG.md
README.md
docs/
what_changed.md
```

Check that documentation matches implemented behavior and does not claim unfinished fidelity/signing/accessibility/stress work.

## 3. Source quality gate

For the exact candidate commit:

```bash
ruff check .
black --check --diff .
mypy src/docmergeforge
pytest --cov=docmergeforge --cov-report=term-missing
```

Required CI evidence:

- Quality workflow green on Python 3.12;
- Quality workflow green on Python 3.13 (while supported by the project CI matrix).

Any code change made after this evidence invalidates it for the new head and requires new runs.

## 4. 120-part regression gate

The exact release head should pass:

- generated SQL 120-part fixture creation;
- integration/regression tests;
- CLI Parts 1–120 validation.

A green synthetic 120-part regression proves the configured workflow remains functional at that fixture scale. It does not prove multi-gigabyte real-world fidelity/performance.

## 5. Cross-platform Build Smoke gate

The exact release head should pass Build Smoke on:

- Ubuntu;
- Windows;
- macOS.

Required checks include:

- source compile;
- CLI help/entry point;
- accessibility smoke;
- packaging preflight.

## 6. Security gate

For the release head:

- CodeQL should complete successfully;
- dependency changes should receive dependency-review evidence in PR context where applicable;
- security-sensitive code changes should have focused regression tests;
- no secrets/private manuscripts are present in the repository or fixtures.

Review open security advisories for direct dependencies before stable distribution.

## 7. Recovery acceptance gate

Automated tests should be green for:

- transactional mixed PDF/DOCX publication;
- report-generation failure before promotion;
- cancellation paths;
- output writeability failure;
- disk-exhaustion simulation;
- rollback behavior;
- journal recovery;
- fingerprint mismatch fail-closed behavior.

For stable production acceptance, also perform controlled real process termination during promotion on disposable test data and verify `recover-output` restores a coherent pre-publication state.

Perform this on each target filesystem/OS class where publication is claimed.

## 8. Stress gate

Run the manual stress workflow at a scale appropriate to release claims.

Record:

- fixture parameters;
- source byte size;
- final PDF/DOCX sizes;
- elapsed behavior/resource observations where measured;
- validation result;
- compare result;
- cancellation/recovery behavior if tested;
- workflow run ID/artifact hashes.

Do not claim “multi-gigabyte tested” unless an actual measured multi-gigabyte run completed successfully.

## 9. Real-world fidelity gate

Synthetic fixtures are insufficient for advanced DOCX/PDF fidelity.

Maintain a privacy-safe acceptance corpus covering, where applicable:

### PDF

- bookmarks/outlines;
- metadata;
- encrypted inputs;
- rotated/cropped pages;
- mixed page sizes;
- images/transparency;
- generated title/TOC/numbering/header/footer/watermark.

### DOCX

- headings/styles;
- tables;
- images;
- sections/page setup;
- headers/footers;
- page numbering;
- numbered/bulleted lists;
- footnotes/endnotes where relevant;
- fields/TOC;
- equations/content controls/custom XML/relationships where relevant;
- track-changes/OLE/macro-adjacent risk documents where policy requires review.

Open final DOCX in the actual target office applications and record human acceptance.

Portable mode must remain the stated production path until high-fidelity external-suite adapters have their own verified implementation/acceptance.

## 10. Accessibility gate

Automated cross-platform metadata smoke must pass.

Before a stable release, complete human acceptance for representative workflows:

- keyboard-only operation;
- Windows screen reader(s);
- macOS VoiceOver;
- supported Linux assistive technology if Linux GUI accessibility is claimed;
- high contrast/theme modes;
- increased text/display scaling;
- reduced-motion preference;
- long paths/large lists/errors/progress dialogs.

Record defects and rerun after fixes.

## 11. Package build gate

Trigger `Package Desktop` for the exact release commit/tag.

Verify that Windows/macOS/Linux PyInstaller builds are created.

Current CI archives are explicitly named as unsigned development artifacts. They are not the final production authenticity gate.

## 12. Packaged-app acceptance

On clean machines/VMs (not developer environments), test the packaged app:

1. launch desktop UI;
2. create/open project;
3. run validation/preflight;
4. merge representative PDF;
5. merge representative DOCX;
6. run mixed project publication;
7. test encrypted PDF;
8. test cancellation;
9. test interrupted-output recovery where possible;
10. inspect generated reports;
11. run audit/compare;
12. verify branding/resources;
13. verify Unicode/long/space-containing paths.

A packaging preflight alone is not sufficient.

## 13. Platform signing/distribution gate

### Windows

Production distribution should verify:

- code-signing certificate/identity;
- executable/installer signature;
- timestamping;
- clean-machine trust behavior;
- installer upgrade/uninstall behavior if an installer is used.

### macOS

Verify:

- Developer ID signing;
- hardened runtime/entitlements as required;
- notarization;
- stapling;
- Gatekeeper verification on a clean machine.

### Linux

Define and verify the actual distribution mechanism and compatibility baseline. If distro-native packages/repositories are used, sign/publish them according to that ecosystem.

Never store production signing credentials in the repository.

## 14. Generate release hashes

For every distributed artifact, generate SHA-256 and preserve it in release records.

Record at minimum:

- artifact filename;
- byte size;
- SHA-256;
- build workflow run;
- commit/tag;
- signing/notarization status.

## 15. Final documentation review

Review:

- installation;
- getting started;
- CLI reference;
- desktop guide;
- recovery;
- executable building;
- known limitations;
- privacy/security;
- release notes/changelog;
- support/contact information.

Every command shown in docs should match the shipped version.

## 16. Tag and GitHub release

Create the semantic version tag only for the chosen release commit.

The existing Package Desktop workflow triggers on `v*` tags, so ensure the tag points to the intended code before pushing.

Release notes should include:

- version/date;
- major changes;
- compatibility notes;
- known limitations;
- verification summary;
- artifact hashes;
- signing status;
- upgrade/recovery notes where relevant;
- links to documentation.

## 17. Post-release verification

After publishing:

- download artifacts as an end user would;
- verify hashes/signatures;
- launch/install on clean machines;
- confirm release notes/docs links;
- confirm no debug/private artifacts were uploaded;
- monitor issue/security reports;
- preserve workflow/acceptance evidence.

## Stable `v1.0.0` gate

Do not claim stable `v1.0.0` until at least these areas are intentionally accepted:

- core PDF/DOCX merge correctness;
- project/CLI/desktop workflows;
- source-integrity and transactional publication;
- journal recovery and forced-interruption acceptance;
- representative large/stress workloads;
- real-world PDF/DOCX fidelity corpus;
- accessibility human acceptance;
- cross-platform packaged-app acceptance;
- Windows/macOS production signing/notarization where those platforms are distributed;
- documentation/support/security processes.

## Release evidence template

Record a release checkpoint in a form similar to:

```text
Version/tag:
Commit SHA:
Date:
Quality run:
120-Part Regression run:
Build Smoke run:
Security run:
Stress run(s):
Package Desktop run:
Windows packaged acceptance:
Windows signature verification:
macOS packaged acceptance:
macOS notarization verification:
Linux packaged acceptance:
Accessibility acceptance record:
Fidelity corpus result:
Recovery interruption result:
Artifact SHA-256 values:
Known limitations:
Release approver/notes:
```

This evidence makes future debugging and release comparison substantially easier.
