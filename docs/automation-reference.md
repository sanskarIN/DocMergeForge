# Automation and Workflow Reference

This document is the canonical guide to the repository automation under `scripts/` and `.github/workflows/`. It explains what each automation entry point is responsible for, where it runs, what evidence it can produce, and what it **does not** prove by itself.

For the literal repository-wide file inventory, see [Complete Repository File Reference](repository-reference.md). For test ownership, see [Test Suite Reference](test-suite-reference.md).

## Automation principles

DocMergeForge automation follows these rules:

1. A script or workflow being present is not evidence that its latest run passed.
2. A passing synthetic test is not automatically proof of real-world office/document fidelity.
3. Native LibreOffice and Microsoft Word lanes remain acceptance/prototype evidence until the documented production gates are completed.
4. Release packaging and provenance do not substitute for signing, notarization, clean-machine testing, or human acceptance.
5. Destructive or expensive acceptance work should remain explicitly invoked where appropriate.
6. CI must fail closed when lint, type, tests, documentation integrity, or required artifact checks fail.

## Script entry points

### `scripts/build_desktop.py`

Purpose: build the desktop application using the maintained packaging configuration instead of duplicating raw PyInstaller arguments in multiple places.

Typical use:

```bash
python scripts/build_desktop.py
```

The script delegates build-command construction to the runtime packaging layer so tests can verify the build contract independently of actually producing an executable.

Evidence boundary: a successful invocation/build proves the configured build path completed on that environment. It does not prove clean-machine compatibility, signing, notarization, installer quality, or human usability.

### `scripts/check_accessibility.py`

Purpose: perform automated static checks for maintained accessibility expectations in the PySide6 UI code.

Typical use:

```bash
python scripts/check_accessibility.py
```

This is useful for catching regressions in labels, accessible names, keyboard affordances, and other machine-checkable UI properties.

Evidence boundary: static checks do not replace keyboard-only, screen-reader, high-contrast, display-scaling, reduced-motion, or localization-readiness human acceptance.

### `scripts/check_disk_full_recovery.py`

Purpose: exercise output publication and recovery behavior under controlled exhausted-storage conditions.

The harness exists because ordinary unit tests cannot fully represent the operational behavior of storage failures during a publication transaction.

Evidence boundary: controlled disk-full simulation does not establish behavior for every physical storage device failure, sudden power loss, network filesystem, or multi-host concurrency condition.

### `scripts/check_docs_links.py`

Purpose: scan local Markdown links and fail when a repository-relative target does not exist.

Typical use:

```bash
python scripts/check_docs_links.py
```

The default root is the repository root. `--root` can target another checkout when testing the checker itself.

This command is part of the primary Quality workflow.

### `scripts/check_repository_reference.py`

Purpose: enforce that every Git-tracked file is explicitly named in `docs/repository-reference.md`.

Typical use:

```bash
python scripts/check_repository_reference.py
```

The check uses `git ls-files`, so generated/untracked local files are intentionally excluded. A new committed path must be documented in the repository reference in the same change.

Evidence boundary: coverage means the file is explicitly cataloged; it does not automatically prove the prose description is semantically complete. Review remains responsible for description accuracy.

### `scripts/check_docx_fidelity_acceptance.py`

Purpose: run the maintained DOCX fidelity acceptance evaluator and emit reviewable evidence about supported structural/content expectations.

Use this when validating adapter changes or expanding the fidelity corpus.

Evidence boundary: acceptance output should be interpreted using `docs/docx-fidelity-acceptance.md`; it is not permission to enable a native adapter's production flag without the corresponding full acceptance matrix.

### `scripts/check_libreoffice_uno_merge_acceptance.py`

Purpose: drive the supervised LibreOffice UNO multi-document acceptance path.

The command validates prerequisites, invokes the maintained acceptance orchestration, and reports structured evidence for the UNO path.

Use only on an environment where LibreOffice/UNO is intentionally available and acceptance execution is appropriate.

### `scripts/check_libreoffice_uno_merge_smoke.py`

Purpose: run a focused supervised LibreOffice UNO merge smoke scenario.

This is narrower and faster than the broader acceptance command and is useful for process/startup/integration diagnostics.

Evidence boundary: smoke success is not equivalent to representative fidelity acceptance.

### `scripts/check_project_sync.py`

Purpose: evaluate reusable project synchronization drift without mutating the project file.

Typical use:

```bash
python scripts/check_project_sync.py path/to/project.json
```

The script is suitable for CI or local maintenance when a project should remain synchronized with numbered/in-range files in its source tree.

Mutation belongs to the guarded `docmergeforge project-sync` CLI workflow, where preview, apply, removals approval, stale-plan protection, and backups are maintained.

### `scripts/check_word_native_merge_acceptance.py`

Purpose: drive controlled Microsoft Word native merge acceptance on a Windows environment where Word automation is deliberately available.

Evidence boundary: this is not a portable CI lane and does not make Word a production-ready adapter by itself.

### `scripts/check_word_native_merge_smoke.py`

Purpose: run a smaller Word native merge smoke scenario for controlled environment validation and diagnosis.

Use it before or alongside broader acceptance when isolating Word automation problems.

### `scripts/check_word_process_state.ps1`

Purpose: capture Windows process-state evidence relevant to Word native acceptance and cleanup verification.

The PowerShell helper supports determining whether automation left Word-related processes behind after normal or failure paths.

### `scripts/check_word_timeout_cleanup_acceptance.py`

Purpose: exercise the controlled Word timeout path and verify the maintained process-cleanup expectations.

This is intentionally separated from a normal successful merge so timeout cleanup can be inspected as its own acceptance gate.

### `scripts/generate_120_fixture.py`

Purpose: create a deterministic synthetic 120-part publication fixture for large numbered-part regression testing.

The generated fixture is test data, not a representative real-world fidelity corpus.

### `scripts/generate_stress_fixture.py`

Purpose: create configurable large/stress input sets for resource and throughput testing.

Use with the resource-evidence wrapper or Stress workflow when collecting measured stress evidence.

### `scripts/report_word_acceptance_environment.ps1`

Purpose: record controlled environment information for Microsoft Word acceptance runs.

Environment evidence is important because native-office behavior can vary with OS/Office versions and configuration. The report should accompany, not replace, the actual acceptance results.

### `scripts/run_with_resource_evidence.py`

Purpose: execute another command while measuring and recording resource/runtime evidence.

This wrapper supports stress/release evidence that needs observed values instead of estimates.

### `scripts/write_build_provenance.py`

Purpose: create the maintained build-provenance manifest for packaged artifacts.

The manifest can include build/runtime metadata and artifact hashes so a release bundle can be traced to its build context.

Evidence boundary: provenance is not a digital signature and does not establish publisher identity or notarization.

## GitHub Actions workflows

### `Quality` — `.github/workflows/quality.yml`

Triggers: pushes to `main` and pull requests.

Platform: Ubuntu, matrix across Python 3.12 and 3.13.

Maintained checks include:

- installation of development dependencies;
- pre-commit configuration validation;
- Ruff linting;
- Black format verification;
- strict mypy checking of `src/docmergeforge`;
- local Markdown link validation;
- complete repository-reference coverage validation;
- pytest with coverage reporting.

This is the primary source-quality gate. A file being committed is not proof that this workflow has passed for that commit; inspect the actual run/status before recording green evidence.

### `120-Part Regression` — `.github/workflows/regression.yml`

Purpose: run the maintained larger regression suite, including numbered multi-part publication behavior that should remain stable beyond ordinary unit tests.

This lane protects high-volume logical behavior but is still synthetic unless a test explicitly uses real representative documents.

### `Build Smoke` — `.github/workflows/build-smoke.yml`

Purpose: verify the maintained desktop build path can produce a development executable/package artifact in CI.

Use it to catch packaging configuration/import regressions early.

Evidence boundary: build smoke does not establish signed production distribution readiness.

### `Security` — `.github/workflows/security.yml`

Purpose: run the repository's automated security-oriented checks/analysis.

Treat a successful workflow as one layer of defense, not a claim that the application is vulnerability-free.

### `Recovery Acceptance` — `.github/workflows/recovery-acceptance.yml`

Purpose: validate interrupted publication/recovery behavior at an acceptance level beyond isolated unit tests.

This lane should remain aligned with `docs/recovery.md` and the transactional guarantees documented for output publication.

### `Disk Full Acceptance` — `.github/workflows/disk-full-acceptance.yml`

Purpose: validate controlled exhausted-storage behavior and recovery expectations.

This workflow covers a specific operational failure mode and should not be generalized to untested storage failures.

### `DOCX Fidelity Acceptance` — `.github/workflows/fidelity-acceptance.yml`

Purpose: run maintained DOCX fidelity checks and acceptance evidence generation.

This supports portable/fidelity development but does not, by itself, enable LibreOffice or Word production readiness.

### `LibreOffice UNO Acceptance` — `.github/workflows/libreoffice-uno-acceptance.yml`

Purpose: run supervised native LibreOffice UNO multi-document acceptance on an Ubuntu environment with the required office dependencies.

The workflow is intended to gather real UNO behavior rather than merely test mocks. Results must still be interpreted against section/page-layout, OOXML-risk, rendering/interoperability, and representative-corpus requirements.

### `LibreOffice UNO Process Cleanup` — `.github/workflows/libreoffice-uno-process-cleanup.yml`

Purpose: exercise real process-group cleanup behavior independently from normal merge fidelity.

Separating cleanup makes it easier to prove that timeout/failure safety remains correct without conflating it with document-content acceptance.

### `Onefile Acceptance` — `.github/workflows/onefile-acceptance.yml`

Purpose: build/test the PyInstaller one-file execution surface and its packaged runtime/resource behavior.

This lane protects the single-file executable mode, not signing/notarization or native installer behavior.

### `Package Desktop` — `.github/workflows/package.yml`

Purpose: create platform packaging artifacts and associated release metadata/evidence such as hashes, SBOM/provenance outputs, and smoke verification according to the workflow definition.

The canonical operator material is under `docs/build/` and `docs/release-packaging.md`.

Evidence boundary: unsigned CI artifacts remain unsigned development artifacts unless separate signing/notarization evidence exists.

### `Project Sync Safety` — `.github/workflows/project-sync-safety.yml`

Purpose: run cross-platform project synchronization safety coverage, including path/selection and drift-related behavior that can vary by operating system.

This workflow is especially important for platform-aware path identity and safe maintenance of explicit selected-file lists.

### `Stress Acceptance` — `.github/workflows/stress.yml`

Purpose: manually execute large/stress scenarios and collect resource evidence under controlled parameters.

Manual dispatch is appropriate because stress workloads can be expensive and should be intentional.

Evidence boundary: only measured values from an actual run should be recorded. Do not turn configured target sizes into claimed observed performance.

### `Word Native Acceptance` — `.github/workflows/word-native-acceptance.yml`

Purpose: run controlled native Microsoft Word acceptance on an intentionally prepared self-hosted Windows/Word runner.

The workflow contains normal merge and timeout-cleanup stages so both fidelity-oriented behavior and cleanup behavior can be evaluated.

Security/operations boundary: self-hosted runner preparation, Word licensing/configuration, repository trust, and credential hygiene are operator responsibilities. The workflow should not be enabled on an untrusted general-purpose host.

Production boundary: successful automation is still only one part of the documented Word production gate; representative corpus and human rendering/behavior acceptance remain required.

## Workflow-to-document map

| Automation area | Canonical documentation |
| --- | --- |
| Quality/lint/type/tests | [Testing and CI](testing-and-ci.md) |
| Documentation integrity | [Documentation Catalog](documentation-catalog.md) and [Complete Repository File Reference](repository-reference.md) |
| Recovery | [Publication Recovery](recovery.md) |
| Disk-full behavior | [Stress Testing](stress-testing.md) and [Publication Recovery](recovery.md) |
| DOCX fidelity | [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md) |
| LibreOffice native | [LibreOffice Native Multi-Document Merge Acceptance](libreoffice-native-merge-acceptance.md) |
| Word native | [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md) |
| Word timeout cleanup | [Microsoft Word Timeout Cleanup Acceptance](word-timeout-cleanup-acceptance.md) |
| Project synchronization | [Project Synchronization](project-sync.md), [Project Sync CI](project-sync-ci.md) |
| Stress/resource evidence | [Stress Testing](stress-testing.md) |
| Desktop executable builds | [Executable Build Manual](build/README.md) |
| Packaging | [Release Packaging](release-packaging.md) |
| Provenance | [Build Provenance](build/provenance.md) |
| Release readiness | [Release Process](release-process.md), [Release Evidence Ledger](release-evidence.md) |

## Adding a new script or workflow

A new automation file is not complete until:

1. its purpose and safe operating assumptions are documented here;
2. the path is added to `docs/repository-reference.md`;
3. direct unit/integration tests are added where practical;
4. existing CI is updated if the automation is intended to be a required gate;
5. operator-facing docs are updated if the command changes a supported workflow;
6. `what_changed.md` records the development-pass change;
7. actual run evidence is recorded separately from implementation when release claims depend on it.
