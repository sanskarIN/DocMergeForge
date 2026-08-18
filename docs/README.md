# DocMergeForge Documentation

This directory is the canonical documentation set for DocMergeForge. It covers end-user operation, CLI automation, desktop workflows, architecture, document engines, recovery, testing, packaging, release acceptance, privacy, and project maintenance.

> **Made by the Sanskar** · [Buy Me a Coffee](https://buymeacoffee.com/sanskarIN)

## Start here

- [Installation](installation.md) — install from source and prepare a development environment.
- [Getting Started](getting-started.md) — complete first merge from discovery to verified outputs.
- [Desktop User Guide](desktop-guide.md) — GUI workflows, ordering, settings, progress, reports, and recovery.
- [CLI Reference](cli-reference.md) — every supported command and option.
- [Troubleshooting](troubleshooting.md) — common failures and safe recovery actions.

## Core concepts and operation

- [Architecture](architecture.md)
- [Merge Pipeline](merge-pipeline.md)
- [Project Files](project-files.md)
- [Discovery and Ordering](discovery-and-ordering.md)
- [Validation and Preflight](validation-and-preflight.md)
- [Output Artifacts](output-artifacts.md)
- [Publication Recovery](recovery.md)
- [Companion Code Policy](companion-code.md)
- [Audit and Compare](audit-and-compare.md)

## Configuration and diagnostics

- [Application Settings Reference](settings-reference.md)
- [Diagnostics and Logging](diagnostics.md)

## Document engines

- [PDF Engine](pdf-engine.md)
- [DOCX Engine](docx-engine.md)
- [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md)
- [LibreOffice Native Multi-Document Merge Acceptance](libreoffice-native-merge-acceptance.md)
- [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md)
- [Microsoft Word Timeout Cleanup Acceptance](word-timeout-cleanup-acceptance.md)
- [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md)
- [SQL Full Mastery 120-Part Preset](sql-full-mastery-preset.md)

## Safety, privacy, and accessibility

- [Privacy](privacy.md)
- [Security Model](security.md)
- [Accessibility](accessibility.md)
- [Known Limitations](known-limitations.md)

## Building executables

- **[Complete Executable Build Manual](build/README.md)** — canonical build portal.
- [Building Executables Overview](building-executables.md)
- [Common Build Guide](build/common.md)
- [Windows Executable Build Guide](build/windows.md)
- [macOS Executable Build Guide](build/macos.md)
- [Linux Executable Build Guide](build/linux.md)
- [CI Packaging Guide](build/ci-packaging.md)
- [Build Provenance](build/provenance.md)
- [Signing and Notarization](build/signing-and-notarization.md)
- [Executable Verification](build/verification.md)
- [Executable Build Troubleshooting](build/troubleshooting.md)
- [Executable Release Build Checklist](build/release-checklist.md)

## Development, testing, and releasing

- [Development Guide](development.md)
- [Testing and CI](testing-and-ci.md)
- [Stress Testing](stress-testing.md)
- [Release Packaging](release-packaging.md)
- [Release Process](release-process.md)
- [Release Evidence Ledger](release-evidence.md)
- [Operator Runbook](operator-runbook.md)
- [Development Phases](development-phases.md)

## Reference

- [FAQ](faq.md)
- [Glossary](glossary.md)
- [Support](support.md)
- [Repository changelog](../CHANGELOG.md)
- [Current development record](../what_changed.md)
- [Contributing](../CONTRIBUTING.md)
- [Security policy](../SECURITY.md)
- [Third-party notices](../THIRD_PARTY_NOTICES.md)
- [MIT License](../LICENSE)

## Project guarantees

DocMergeForge is designed around a few non-negotiable rules:

1. PDF manuscripts merge only with PDF manuscripts.
2. DOCX manuscripts merge only with DOCX manuscripts.
3. Companion/source-code archives are indexed but never merged into manuscripts.
4. Natural numeric ordering is validated before publication.
5. Source hashes are checked so changed inputs cannot silently become part of a completed run.
6. Final publication files are staged and promoted transactionally.
7. Interrupted promotion evidence is preserved and recovered explicitly rather than guessed away.
8. Documents remain local by default; encrypted-PDF passwords are not persisted by the application.
9. A successful library call is not treated as sufficient validation; outputs are reopened and checked.
10. Unsigned development packages are not represented as signed production releases.

## Supported execution surfaces

DocMergeForge currently exposes:

- the `docmergeforge` command-line application;
- the `docmergeforge-gui` PySide6 desktop application;
- reusable JSON project files;
- the SQL Full Mastery 120-part guided preset;
- PyInstaller-based desktop packaging helpers;
- automated Quality, Regression, Build Smoke, Security, Recovery Acceptance, Disk Full Acceptance, DOCX Fidelity Acceptance, Package Desktop, and Onefile Acceptance workflows;
- a supervised Ubuntu LibreOffice UNO multi-document acceptance workflow plus an independent real process-group-cleanup lane;
- a manually dispatchable Stress Acceptance workflow; and
- a manual controlled self-hosted Microsoft Word Native Acceptance workflow containing both normal merge and controlled timeout-cleanup stages.

## Documentation accuracy policy

Documentation should describe implemented behavior, not aspirational behavior. LibreOffice has a source-preserving one-document round-trip adapter plus a supervised POSIX UNO multi-document **acceptance prototype** with source-revision, body-structure/text, OOXML-risk, isolated-profile, and exact process-group safeguards. Its production mode remains disabled until real workflow evidence, broader section/page-layout fidelity, representative corpora, application integration, and human rendering/interoperability acceptance are complete.

Microsoft Word has a source-preserving round-trip adapter plus a native multi-document **acceptance prototype** with measured section/page-number/source-revision/process-cleanup safeguards and a dedicated controlled timeout-cleanup harness. Its production mode remains disabled until real controlled Word execution, representative corpus, packaged integration, and human rendering/behavior acceptance are verified.

Availability or automation readiness must never be treated as production readiness. See [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md), [LibreOffice Native Multi-Document Merge Acceptance](libreoffice-native-merge-acceptance.md), [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md), [Microsoft Word Timeout Cleanup Acceptance](word-timeout-cleanup-acceptance.md), and [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md).

Executable documentation follows the same rule: current PyInstaller and unsigned CI packaging are documented as implemented and independently smoke-tested, while code signing, notarization, native installer formats, human clean-machine QA, and production distribution remain explicit gates until corresponding acceptance exists.

When code changes behavior, update the relevant guide and `what_changed.md` in the same development cycle. Significant release evidence should also be recorded in [Release Evidence Ledger](release-evidence.md).
