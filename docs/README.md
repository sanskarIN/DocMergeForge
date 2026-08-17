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
- automated Quality, Regression, Build Smoke, Security, and manual Stress workflows.

## Documentation accuracy policy

Documentation should describe implemented behavior, not aspirational behavior. Features that are capability-detected but not production-ready—such as high-fidelity LibreOffice or Microsoft Word automation—must remain clearly marked as incomplete until their adapters and acceptance tests are finished.

Executable documentation follows the same rule: current PyInstaller and unsigned CI packaging are documented as implemented, while code signing, notarization, and native installer formats remain explicit production steps until corresponding automation and acceptance exist.

When code changes behavior, update the relevant guide and `what_changed.md` in the same development cycle.
