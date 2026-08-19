# Documentation Catalog

This catalog maps every maintained documentation file to its intended audience and task. Use it when you know **what you are trying to do** but are not sure which guide is authoritative.

For every tracked repository file, not only documentation, see [Complete Repository File Reference](repository-reference.md).

## First-time users

### `docs/installation.md` — Installation

Audience: users and developers installing from source.

Use it for Python requirements, environment creation, dependency installation, editable installs, optional development/build extras, and first installation checks.

### `docs/getting-started.md` — Getting Started

Audience: new users who want their first successful publication merge.

Use it for the shortest end-to-end path from source selection through ordering, preflight, merge, and output verification.

### `docs/desktop-guide.md` — Desktop User Guide

Audience: GUI users.

Use it for the PySide6 application: source selection, projects, ordering, dry run, settings, merge progress, reports, recent projects, support, and recovery-facing UI behavior.

### `docs/cli-reference.md` — CLI Reference

Audience: terminal users, automation authors, and maintainers.

Use it for every supported command, option, structured output convention, and CLI exit behavior.

### `docs/faq.md` — FAQ

Audience: all users.

Use it when a common capability, limitation, workflow, privacy, fidelity, or packaging question does not require the full subsystem guide.

### `docs/troubleshooting.md` — Troubleshooting

Audience: users/operators diagnosing failed merges or setup/runtime problems.

Use it for symptom-oriented diagnosis and safe corrective actions.

## Core workflow and architecture

### `docs/architecture.md` — Architecture

Audience: developers and advanced operators.

Use it to understand component boundaries, dependency direction, data flow, document engines, transactional publication, validation, project persistence, and desktop/CLI separation.

### `docs/merge-pipeline.md` — Merge Pipeline

Audience: users, developers, and reviewers.

Use it for the exact conceptual stages from discovery and ordering through preflight, merge, staging, promotion, validation, reporting, and recovery evidence.

### `docs/discovery-and-ordering.md` — Discovery and Ordering

Audience: users and developers dealing with large multi-part source trees.

Use it for recursive scanning, supported formats, exclusions, part-number detection, natural numeric order, duplicate/path handling, explicit selections, and manual reorder behavior.

### `docs/validation-and-preflight.md` — Validation and Preflight

Audience: users, developers, and operators.

Use it for source eligibility, expected part ranges, format separation, storage/output checks, encrypted inputs, warnings/errors, and post-merge validation expectations.

### `docs/output-artifacts.md` — Output Artifacts

Audience: users/operators.

Use it to identify final manuscript files, reports, companion archives, transaction artifacts, backups, provenance/evidence files, and which generated files are temporary versus durable.

### `docs/recovery.md` — Publication Recovery

Audience: operators and developers.

Use it for interrupted output transactions, staging directories, journals, promotion checkpoints, backups, rollback/recovery rules, durability boundaries, and fail-closed handling of malformed recovery state.

### `docs/operator-runbook.md` — Operator Runbook

Audience: anyone running important production-like merges or acceptance work.

Use it as an operational checklist before, during, and after a merge, especially when evidence, backups, diagnostics, and reproducibility matter.

## Project files and maintenance

### `docs/project-files.md` — Project Files

Audience: users/developers working with reusable JSON projects.

Use it for project schema, versions, paths, explicit selected files, expected ranges, output configuration, persistence semantics, validation, migration, and recovery checkpoint information.

### `docs/project-sync.md` — Project Synchronization

Audience: users/operators maintaining a saved project as numbered source files change.

Use it for preview-first synchronization, proposed selection/order, added/removed/reordered evidence, explicit apply, second approval for removals, versioned backups, stale-plan protection, and limits of automatic synchronization.

### `docs/project-sync-check-script.md` — Project Sync Check Script

Audience: developers/operators who need a read-only drift check outside the normal CLI workflow.

Use it for `scripts/check_project_sync.py`, expected exit behavior, and automation usage.

### `docs/project-sync-ci.md` — Project Sync CI

Audience: maintainers integrating saved-project drift checks into CI.

Use it for deciding which project files should be checked and how to interpret drift without automatically mutating committed state.

## PDF documentation

### `docs/pdf-engine.md` — PDF Engine

Audience: users/developers with PDF publications.

Use it for PDF merging, encrypted files/password handling, page/metadata validation, output behavior, rendering checks, and known PDF-specific limitations.

## DOCX and fidelity documentation

### `docs/docx-engine.md` — DOCX Engine

Audience: users/developers with Word/DOCX publications.

Use it for the portable DOCX path, merge behavior, publication features, OOXML preservation boundaries, adapter selection, and validation.

### `docs/docx-fidelity-acceptance.md` — DOCX Fidelity Adapters and Acceptance

Audience: maintainers evaluating document fidelity.

Use it for fidelity profiles, adapter capability/readiness states, acceptance evidence, and the rules preventing availability from being confused with production readiness.

### `docs/docx-fidelity-corpus.md` — Private DOCX Fidelity Corpus Testing

Audience: maintainers running representative/private document acceptance.

Use it for corpus organization, privacy expectations, fixture manifests, evidence recording, and how private real-world documents complement public synthetic tests.

### `docs/libreoffice-native-merge-acceptance.md` — LibreOffice Native Multi-Document Merge Acceptance

Audience: maintainers of the LibreOffice UNO prototype.

Use it for supervised UNO execution, isolated profiles, structural/source-revision/risk evidence, process cleanup, platform requirements, current gaps, and the requirements that must be met before production readiness could change.

### `docs/word-native-merge-acceptance.md` — Microsoft Word Native Merge Acceptance

Audience: maintainers with a controlled Windows/Microsoft Word environment.

Use it for native Word multi-document merge acceptance, section/page-number/source evidence, process ownership/cleanup, workflow execution, and remaining production gates.

### `docs/word-timeout-cleanup-acceptance.md` — Microsoft Word Timeout Cleanup Acceptance

Audience: maintainers testing Word automation failure behavior.

Use it specifically for controlled timeout injection, owned-process cleanup, environment evidence, and failure-path acceptance.

### `docs/sql-full-mastery-preset.md` — SQL Full Mastery 120-Part Preset

Audience: users of the guided SQL publication preset.

Use it for preset assumptions, expected source naming/range, guided defaults, output behavior, and when to choose a general project instead.

## Audit, diagnostics, and support

### `docs/audit-and-compare.md` — Audit and Compare

Audience: authors/reviewers checking a publication before or after merge.

Use it for document/publication audits, repeated-content detection, comparisons, and interpreting audit evidence.

### `docs/diagnostics.md` — Diagnostics and Logging

Audience: users, support, and developers.

Use it for log locations, redaction, diagnostic exports, what information is safe/useful to share, and limitations of diagnostics.

### `docs/support.md` — Support

Audience: users who need help.

Use it for support channels, what evidence to include, privacy-safe reporting, and how to distinguish usage questions, bugs, and security reports.

### `docs/glossary.md` — Glossary

Audience: all readers.

Use it when project terms such as preflight, staging, promotion, fidelity adapter, project synchronization, or acceptance evidence are unfamiliar.

## Security, privacy, accessibility, and limitations

### `docs/privacy.md` — Privacy

Audience: all users and reviewers.

Use it for the local-first processing model, persisted versus non-persisted data, passwords, logs, diagnostic exports, native office tools, and privacy boundaries.

### `docs/security.md` — Security Model

Audience: developers/security reviewers/operators.

Use it for trust boundaries, path/symlink handling, atomic writes, transactions, lock files, recovery validation, process supervision, external applications, and threat assumptions.

The root `SECURITY.md` is the vulnerability-reporting policy; this file is the technical model.

### `docs/accessibility.md` — Accessibility

Audience: users, UI developers, and release reviewers.

Use it for implemented accessibility behavior, automated coverage, keyboard/accessibility design expectations, and the human acceptance still required.

### `docs/known-limitations.md` — Known Limitations

Audience: all users and release reviewers.

Use it before relying on advanced DOCX fidelity, office automation, packaging, accessibility, filesystems, or distribution behavior. Unsupported and unverified behavior should remain visible here rather than hidden behind optimistic wording elsewhere.

## Developer documentation

### `docs/development.md` — Development Guide

Audience: contributors and maintainers.

Use it for environment setup, repository layout, common commands, style/type rules, testing, documentation responsibilities, and safe contribution practices.

### `docs/source-code-reference.md` — Source Code Reference

Audience: maintainers working inside `src/docmergeforge`.

Use it for module-by-module runtime responsibilities, architectural dependency direction, safety boundaries, and the change checklist for runtime code.

### `docs/test-suite-reference.md` — Test Suite Reference

Audience: contributors deciding where/how to test a change.

Use it for the complete test-file map, what each unit/integration/regression file protects, acceptance distinctions, and test placement guidance.

### `docs/automation-reference.md` — Automation and Workflow Reference

Audience: maintainers and release operators.

Use it for every script and GitHub Actions workflow, including purpose, operating environment, evidence boundary, and links to canonical subsystem docs.

### `docs/configuration-reference.md` — Configuration, Governance, and Asset Reference

Audience: repository maintainers.

Use it before changing `pyproject.toml`, editor/Git/pre-commit configuration, GitHub templates/ownership/dependency automation, root project metadata, or branding assets.

### `docs/repository-reference.md` — Complete Repository File Reference

Audience: maintainers/reviewers.

Use it as the literal tracked-file inventory. Every tracked path must be named there, and CI enforces that coverage with `scripts/check_repository_reference.py`.

### `docs/testing-and-ci.md` — Testing and CI

Audience: contributors and maintainers.

Use it for commands, pytest markers, quality gates, workflow organization, CI interpretation, and the distinction between source tests and external acceptance.

### `docs/stress-testing.md` — Stress Testing

Audience: maintainers evaluating large workloads/resources.

Use it for fixture generation, measured resource evidence, stress workflow operation, interpreting results, and avoiding unmeasured performance claims.

### `docs/development-phases.md` — Development Phases

Audience: maintainers tracking implementation maturity.

Use it to understand what phases are implemented, which acceptance/release gates remain, and which work is intentionally not represented as complete.

## Executable build documentation

### `docs/building-executables.md` — Building Executables Overview

Audience: developers who need a quick packaging orientation.

Use it for the high-level supported packaging approach and links into the canonical build manual.

### `docs/build/README.md` — Complete Executable Build Manual

Audience: maintainers/build operators.

Use it as the canonical build documentation portal.

### `docs/build/common.md` — Common Build Guide

Audience: all build operators.

Use it for platform-neutral prerequisites, environment setup, build process, expected outputs, and shared verification.

### `docs/build/windows.md` — Windows Build Guide

Audience: Windows build operators.

Use it for Windows-specific executable creation, dependencies, verification, and production-signing boundaries.

### `docs/build/macos.md` — macOS Build Guide

Audience: macOS build operators.

Use it for macOS packaging plus signing/notarization/stapling boundaries.

### `docs/build/linux.md` — Linux Build Guide

Audience: Linux build operators.

Use it for Linux packaging dependencies, build execution, and artifact verification.

### `docs/build/ci-packaging.md` — CI Packaging Guide

Audience: maintainers of `.github/workflows/package.yml` and release artifacts.

Use it for CI packaging jobs, artifact layout, environment assumptions, and the evidence produced by automated packaging.

### `docs/build/provenance.md` — Build Provenance

Audience: release operators/reviewers.

Use it for provenance manifest fields, hashes, source/build identity, verification, and the distinction between provenance and signing.

### `docs/build/signing-and-notarization.md` — Signing and Notarization

Audience: production release operators.

Use it for Windows signing and macOS signing/notarization/stapling processes and the evidence required before a release is called signed/notarized.

### `docs/build/verification.md` — Executable Verification

Audience: build/release reviewers.

Use it for artifact hashes, startup/smoke verification, provenance checks, signature checks, and clean-machine verification expectations.

### `docs/build/troubleshooting.md` — Build Troubleshooting

Audience: build operators.

Use it for PyInstaller/dependency/resource/platform build failures rather than general merge troubleshooting.

### `docs/build/release-checklist.md` — Executable Release Build Checklist

Audience: release operators.

Use it as the final packaging/build checklist, while still following the broader release process and evidence ledger.

## Release documentation

### `docs/release-packaging.md` — Release Packaging

Audience: maintainers preparing distributable artifact sets.

Use it for release bundle composition, executable/source artifacts, hashes, provenance, SBOM/evidence, and artifact naming.

### `docs/release-process.md` — Release Process

Audience: release maintainers.

Use it for end-to-end release preparation, quality/acceptance evidence, versioning, tagging, packaging, signing/notarization, verification, and post-release steps.

### `docs/release-evidence.md` — Release Evidence Ledger

Audience: release reviewers and maintainers.

Use it to record **actual evidence** tied to exact commits/environments/runs. Do not record intended workflows or committed test files as if they were passing results.

## Documentation history and repository records

### `docs/history/what_changed-through-2026-08-18.md`

Audience: maintainers researching earlier development decisions.

Use it for detailed development history archived through 2026-08-18.

### `../what_changed.md`

Audience: maintainers continuing the current development pass.

Use it for the active detailed record of additions, hardening, verification status, and remaining gates.

### `../CHANGELOG.md`

Audience: users and developers.

Use it for the durable chronological summary of notable project changes.

### `../PROJECT_STATE.md`

Audience: future maintenance sessions.

Use it as the compact current-state checkpoint, not as a substitute for detailed subsystem docs or evidence.

## Community and policy documents

### `../README.md`

Primary public landing page: purpose, supported workflows, install/use entry points, major limitations, support/funding, and documentation links.

### `../CONTRIBUTING.md`

Contributor policy: environment, style, tests, docs, PR expectations, and release-claim discipline.

### `../SECURITY.md`

Public vulnerability-reporting policy.

### `../CODE_OF_CONDUCT.md`

Community behavior expectations.

### `../THIRD_PARTY_NOTICES.md`

Dependency/license attribution relevant to distribution.

### `../LICENSE`

MIT license.

## Task-oriented lookup

| Goal | Start with | Then read |
| --- | --- | --- |
| Install and merge files | [Installation](installation.md) | [Getting Started](getting-started.md) |
| Use the desktop app | [Desktop User Guide](desktop-guide.md) | [Troubleshooting](troubleshooting.md) |
| Automate from terminal | [CLI Reference](cli-reference.md) | [Validation and Preflight](validation-and-preflight.md) |
| Understand source code | [Source Code Reference](source-code-reference.md) | [Architecture](architecture.md) |
| Add or modify tests | [Test Suite Reference](test-suite-reference.md) | [Testing and CI](testing-and-ci.md) |
| Modify CI/scripts | [Automation and Workflow Reference](automation-reference.md) | [Testing and CI](testing-and-ci.md) |
| Change repo configuration | [Configuration Reference](configuration-reference.md) | [Development Guide](development.md) |
| Confirm every file is documented | [Complete Repository File Reference](repository-reference.md) | run `python scripts/check_repository_reference.py` |
| Diagnose interrupted output | [Publication Recovery](recovery.md) | [Operator Runbook](operator-runbook.md) |
| Investigate DOCX fidelity | [DOCX Engine](docx-engine.md) | [DOCX Fidelity Acceptance](docx-fidelity-acceptance.md) |
| Test LibreOffice native merge | [LibreOffice Acceptance](libreoffice-native-merge-acceptance.md) | [Automation Reference](automation-reference.md) |
| Test Word native merge | [Word Native Acceptance](word-native-merge-acceptance.md) | [Word Timeout Cleanup](word-timeout-cleanup-acceptance.md) |
| Build executables | [Build Manual](build/README.md) | platform guide + [Verification](build/verification.md) |
| Prepare a release | [Release Process](release-process.md) | [Release Evidence](release-evidence.md) |
| Report a problem | [Support](support.md) | [Diagnostics](diagnostics.md) or root `SECURITY.md` |

## Documentation maintenance rule

When behavior changes, update the most specific canonical guide rather than only updating README/changelog text. When a tracked file is added, renamed, or deleted, also update `docs/repository-reference.md`. Run both documentation integrity checks before considering the documentation part of the change complete:

```bash
python scripts/check_docs_links.py
python scripts/check_repository_reference.py
```

Documentation must describe implemented or explicitly proposed/limited behavior accurately. It must not convert the existence of a test, script, workflow, adapter, or build configuration into an unverified claim of passing acceptance or production readiness.
