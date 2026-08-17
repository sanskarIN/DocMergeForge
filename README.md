<p align="center">
  <img src="assets/branding/readme-banner.svg" alt="DocMergeForge banner" width="100%">
</p>

# DocMergeForge

**Discover correctly. Order correctly. Merge safely. Validate everything. Preserve the originals. Keep companion code independent.**

DocMergeForge is a local-first cross-platform desktop and CLI application for assembling very large multi-part publications into validated master PDF and DOCX editions.

> **Made by the Sanskar**

[Buy Me a Coffee](https://buymeacoffee.com/sanskarIN) ·
[GitHub](https://www.github.com/sanskarIN) ·
[LinkedIn](https://www.linkedin.com/in/sanskarIN) ·
[YouTube](https://youtube.com/@Sanskar-in) ·
[X](https://www.x.com/Sanskar_in)

## Documentation

The complete documentation portal is **[docs/README.md](docs/README.md)**.

Start with:

- [Installation](docs/installation.md)
- [Getting Started](docs/getting-started.md)
- [Desktop User Guide](docs/desktop-guide.md)
- [CLI Reference](docs/cli-reference.md)
- [Operator Runbook](docs/operator-runbook.md)
- [Building Executables](docs/building-executables.md)
- [Troubleshooting](docs/troubleshooting.md)

Technical/safety/release references include:

- [Architecture](docs/architecture.md)
- [Merge Pipeline](docs/merge-pipeline.md)
- [PDF Engine](docs/pdf-engine.md)
- [DOCX Engine](docs/docx-engine.md)
- [Project Files](docs/project-files.md)
- [Validation and Preflight](docs/validation-and-preflight.md)
- [Publication Recovery](docs/recovery.md)
- [Output Artifacts](docs/output-artifacts.md)
- [Settings Reference](docs/settings-reference.md)
- [Diagnostics and Logging](docs/diagnostics.md)
- [Security Model](docs/security.md)
- [Privacy](docs/privacy.md)
- [Accessibility](docs/accessibility.md)
- [Testing and CI](docs/testing-and-ci.md)
- [Stress Testing](docs/stress-testing.md)
- [Release Packaging](docs/release-packaging.md)
- [Release Process](docs/release-process.md)
- [Known Limitations](docs/known-limitations.md)

## Core guarantees

- PDF and DOCX pipelines remain separate.
- Natural numeric ordering handles Part 2 before Part 10.
- Original source hashes are captured and checked during publication workflows.
- Companion code archives are indexed but never merged, extracted, rewritten, or refactored by the manuscript pipeline.
- PDF/DOCX outputs are validated before publication.
- Full project outputs and generated evidence are staged and promoted as one transaction.
- Interrupted promotion can be recovered through a durable journal and fail-closed fingerprint checks.
- No manuscript content is uploaded by the normal local-first workflow.
- No DocMergeForge account is required.
- Encrypted-PDF passwords are not persisted by the application.

## SQL Full Mastery preset

The dedicated **SQL Full Mastery — 120-Part Master Edition** preset expects Parts 1–120, validates PDF and DOCX sets independently, creates both master manuscripts, and writes checksums, manifests, reports, a companion-code index, and a publishing checklist.

See [docs/sql-full-mastery-preset.md](docs/sql-full-mastery-preset.md).

## Installation

Python 3.12+:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -e .
```

Developer environment:

```bash
pip install -e ".[dev]"
pre-commit install
pytest
```

Full platform instructions: [docs/installation.md](docs/installation.md).

## GUI

```bash
docmergeforge-gui
```

The desktop application provides project setup, validation/preflight, ordering, merge progress/cancellation, reports, recent projects/recovery, audit/compare, settings, help/support, and SQL preset workflows.

See [Desktop User Guide](docs/desktop-guide.md).

## CLI

Show all commands:

```bash
docmergeforge --help
```

Validate:

```bash
docmergeforge validate --input "./SQL-Full-Mastery" --parts 1-120
```

Merge PDFs:

```bash
docmergeforge pdf \
  --input "./SQL-Full-Mastery" \
  --parts 1-120 \
  --output "./Master/SQL_Full_Mastery_Complete_120_Part_Master_Edition.pdf"
```

Merge DOCX:

```bash
docmergeforge docx \
  --input "./SQL-Full-Mastery" \
  --parts 1-120 \
  --output "./Master/SQL_Full_Mastery_Complete_120_Part_Master_Edition.docx"
```

SQL preset dry run:

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Full-Mastery-Master-Edition" \
  --dry-run
```

Full SQL preset:

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Full-Mastery-Master-Edition"
```

Other commands include reusable project creation/execution, interrupted-output recovery, audit, and output comparison. See the complete [CLI Reference](docs/cli-reference.md).

## Safe interrupted-output recovery

If final publication is interrupted and a `.docmergeforge-staging-*` transaction remains, **do not delete it manually**. It can contain the rollback copy of a previous publication.

Run:

```bash
docmergeforge recover-output --output-dir "./Master"
```

Recovery validates journal state and file fingerprints and fails closed when the filesystem cannot be proven safe. See [Publication Recovery](docs/recovery.md).

## 120-part regression fixture

```bash
python scripts/generate_120_fixture.py fixtures/generated/sql-120
docmergeforge validate --input fixtures/generated/sql-120 --parts 1-120
```

Each generated companion ZIP remains independent from the manuscript.

The repository also provides a manually scalable synthetic stress workflow. A generated 120-part test must not be described as multi-gigabyte acceptance unless the measured generated source size actually reaches that class. See [Stress Testing](docs/stress-testing.md).

## Validation evidence

PDF validation reopens the result and verifies expected page evidence. DOCX validation checks OOXML ZIP/container structure, required members/XML readability, and parser reopen. Full project publication also verifies source integrity before final promotion.

The application does not report success merely because a library call returned.

See [Validation and Preflight](docs/validation-and-preflight.md).

## DOCX fidelity policy

Portable DOCX composition is the current production-supported path. It supports many normal Word structures but cannot prove perfect preservation for every advanced Microsoft Word construct. Macros, OLE objects, tracked changes, complex fields, custom XML, some equations, content controls, external relationships, and complex style/numbering/section behavior require special review.

LibreOffice and Microsoft Word high-fidelity modes are not currently accepted as production-ready adapters and are deliberately prevented from silently replacing portable mode.

See [DOCX Engine](docs/docx-engine.md) and [Known Limitations](docs/known-limitations.md).

## Repository structure

```text
src/docmergeforge/    application source
tests/                unit, integration, regression
scripts/              build, fixture, stress, accessibility tools
docs/                 complete user/operator/developer documentation
assets/branding/      original SVG branding
.github/workflows/    quality, regression, build, security, package, stress automation
```

Architecture details: [docs/architecture.md](docs/architecture.md).

## Quality commands

```bash
ruff check .
black --check --diff .
mypy src/docmergeforge
pytest
```

CI also exercises the generated 120-part regression, cross-platform desktop build/accessibility smoke, CodeQL security analysis, package building, and manually triggered stress acceptance.

See [Testing and CI](docs/testing-and-ci.md).

## Building desktop executables

Install packaging tools:

```bash
pip install -e ".[build]"
```

Validate packaging configuration:

```bash
python scripts/build_desktop.py --check
```

Default onedir development build:

```bash
python scripts/build_desktop.py
```

Optional one-file build:

```bash
python scripts/build_desktop.py --one-file
```

Build Windows on Windows, macOS on macOS, and Linux on Linux/native CI runners. Current CI package archives are explicitly **unsigned development builds**; production signing/notarization remains a separate release gate.

See [Building Executables](docs/building-executables.md) and [Release Packaging](docs/release-packaging.md).

## Privacy and security

Documents stay local under the normal workflow, passwords are not persisted, diagnostics are designed to exclude manuscript body text/passwords, and companion archives are not auto-extracted.

Review paths/filenames in project files, reports, manifests, diagnostics, and audit output before sharing them publicly.

- [Privacy](docs/privacy.md)
- [Security Model](docs/security.md)
- [Security reporting policy](SECURITY.md)
- [Diagnostics and Logging](docs/diagnostics.md)

## Accessibility

Important desktop controls expose explicit accessible metadata and keyboard behavior, with an offscreen accessibility smoke exercised in cross-platform Build Smoke.

Automated metadata checks are not represented as full human accessibility certification; screen-reader/high-contrast/scaling/reduced-motion acceptance remains part of the stable-release gate.

See [Accessibility](docs/accessibility.md).

## Release status

DocMergeForge remains pre-stable. Green source CI and unsigned PyInstaller archives do not by themselves justify a `v1.0.0` production-ready claim.

Open acceptance areas include representative real-world fidelity, large measured stress workloads, real abrupt-process recovery, human accessibility, packaged-app clean-machine acceptance, and platform signing/notarization where distributed.

See [Release Process](docs/release-process.md), [Known Limitations](docs/known-limitations.md), and [what_changed.md](what_changed.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [Development Guide](docs/development.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

MIT — see [LICENSE](LICENSE).

## Support and creator

- Repository: https://github.com/sanskarIN/DocMergeForge
- GitHub: https://www.github.com/sanskarIN
- LinkedIn: https://www.linkedin.com/in/sanskarIN
- **Buy Me a Coffee:** https://buymeacoffee.com/sanskarIN
- YouTube: https://youtube.com/@Sanskar-in
- X: https://www.x.com/Sanskar_in
- Business: `sanskarin@outlook.in`
- Business: `sanskarin.business@gmail.com`
- Support: `supportramsandesh@gmail.com`

Complete support guidance: [docs/support.md](docs/support.md).

**The PDFs are merged. The DOCX files are merged. The code remains separate.**
