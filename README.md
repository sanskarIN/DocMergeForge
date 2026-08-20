<p align="center">
  <img src="assets/branding/readme-banner.svg" alt="DocMergeForge banner" width="100%">
</p>

# DocMergeForge

**Discover correctly. Order correctly. Merge safely. Validate everything. Preserve the originals. Keep companion code independent.**

DocMergeForge is a local-first document-merging toolkit with native desktop/CLI workflows on Windows, macOS, and Linux plus a responsive browser client for Android, iOS/iPadOS, ChromeOS, desktop browsers, and other modern browser platforms connected to a DocMergeForge Python host.

> **Made by the Sanskar**

[Buy Me a Coffee](https://buymeacoffee.com/sanskarIN) ·
[GitHub](https://www.github.com/sanskarIN) ·
[LinkedIn](https://www.linkedin.com/in/sanskarIN) ·
[YouTube](https://youtube.com/@Sanskar-in) ·
[X](https://x.com/x_sanskarIN)

## Documentation

The complete documentation portal is **[docs/README.md](docs/README.md)**. The [Documentation Catalog](docs/documentation-catalog.md) maps every guide by audience and task, while the [Complete Repository File Reference](docs/repository-reference.md) documents every tracked repository file.

Start with:

- [Installation](docs/installation.md)
- [Getting Started](docs/getting-started.md)
- [Platform Support](docs/platform-support.md)
- [Desktop User Guide](docs/desktop-guide.md)
- [CLI Reference](docs/cli-reference.md)
- [Project Synchronization](docs/project-sync.md)
- [Operator Runbook](docs/operator-runbook.md)
- [Building Executables](docs/building-executables.md)
- [Troubleshooting](docs/troubleshooting.md)

Technical/safety/release references include:

- [Architecture](docs/architecture.md)
- [Source Code Reference](docs/source-code-reference.md)
- [Test Suite Reference](docs/test-suite-reference.md)
- [Automation and Workflow Reference](docs/automation-reference.md)
- [Configuration, Governance, and Asset Reference](docs/configuration-reference.md)
- [Complete Repository File Reference](docs/repository-reference.md)
- [Merge Pipeline](docs/merge-pipeline.md)
- [PDF Engine](docs/pdf-engine.md)
- [DOCX Engine](docs/docx-engine.md)
- [DOCX Fidelity Adapters and Acceptance](docs/docx-fidelity-acceptance.md)
- [LibreOffice Native Multi-Document Merge Acceptance](docs/libreoffice-native-merge-acceptance.md)
- [Microsoft Word Native Merge Acceptance](docs/word-native-merge-acceptance.md)
- [Microsoft Word Timeout Cleanup Acceptance](docs/word-timeout-cleanup-acceptance.md)
- [Private DOCX Fidelity Corpus Testing](docs/docx-fidelity-corpus.md)
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
- Native desktop/CLI workflows do not upload manuscript content to a DocMergeForge-operated cloud service.
- Browser mode sends selected files only to the DocMergeForge Python host the user connected to; LAN/remote transport is a separate trust boundary documented below.
- No DocMergeForge account is required.
- Encrypted-PDF passwords are not persisted by the application.
- External DOCX fidelity acceptance writes separate validated copies and never silently changes the production merge mode.
- Maintained native-office acceptance paths remove a newly promoted result if final destination/source verification fails.

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

Developer environment including responsive-web tests:

```bash
pip install -e ".[dev,web]"
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

## Web and mobile-browser access

Install the optional web runtime and start the safest loopback-only host:

```bash
pip install -e ".[web]"
docmergeforge-web
```

Then open:

```text
http://127.0.0.1:8765/
```

For a phone, tablet, Chromebook, or another computer on the same trusted LAN, require token protection:

```bash
docmergeforge-web --host 0.0.0.0 --token auto
```

Open `http://HOST-LAN-IP:8765/` on the other device and enter the generated token in **Access token (LAN only)**. A trusted one-time link may use `#token=YOUR_LONG_RANDOM_TOKEN`; do not use `?token=...`, because query parameters can be recorded in HTTP access logs and surrounding infrastructure.

Browser mode reuses the shared Python PDF/DOCX engines on the selected host. It is not represented as a native Android APK/AAB, native iOS IPA, or fully offline in-browser document engine. Plain HTTP on an untrusted network does not provide transport confidentiality; use HTTPS and a hardened reverse-proxy/authentication layer for traffic outside a trusted local environment.

See [Platform Support](docs/platform-support.md), [Installation](docs/installation.md), and [Security Model](docs/security.md).

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

Preview project selected-file synchronization:

```bash
docmergeforge project-sync --project "./Book.json"
```

Apply a reviewed addition/reorder-only proposal:

```bash
docmergeforge project-sync --project "./Book.json" --apply
```

If the preview reports removals, review them individually before approving both mutation and removals with `--apply --allow-removals`. Synchronization changes project metadata only; it does not delete manuscript source files. See [Project Synchronization](docs/project-sync.md).

Inspect DOCX fidelity capabilities:

```bash
docmergeforge fidelity-capabilities
```

Run one explicit LibreOffice acceptance round trip:

```bash
docmergeforge fidelity-roundtrip \
  --input "./samples/representative.docx" \
  --output "./evidence/representative-libreoffice.docx" \
  --mode libreoffice
```

Run a private local fidelity corpus:

```bash
docmergeforge fidelity-corpus \
  --input-dir "./private-corpus" \
  --output-dir "./private-fidelity-evidence" \
  --mode libreoffice
```

For **non-production native LibreOffice multi-document acceptance** on a POSIX host with Writer + Python UNO installed, use the explicit ordered acceptance script:

```bash
python scripts/check_libreoffice_uno_merge_acceptance.py \
  --input "./private-corpus/Part 1.docx" \
  --input "./private-corpus/Part 2.docx" \
  --output "./private-libreoffice-evidence/merged.docx" \
  --evidence "./private-libreoffice-evidence/evidence.json"
```

This does not change the normal `docmergeforge docx` engine or mark LibreOffice production-ready.

The controlled Word path remains a separate acceptance-only workflow on a dedicated Windows/Word environment; it is not a portable runtime dependency.

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

Portable DOCX composition is the current production-supported multi-document path. It supports many normal Word structures but cannot prove perfect preservation for every advanced Microsoft Word construct. Macros, OLE objects, tracked changes, complex fields, custom XML, equations, content controls, external relationships, charts/SmartArt, and complex style/numbering/section behavior require special review.

DocMergeForge includes explicit source-preserving LibreOffice and Windows Microsoft Word round-trip adapters for fidelity acceptance.

LibreOffice also has a **non-production supervised POSIX Writer/UNO multi-document acceptance prototype**. It uses an isolated user profile, unique UNO pipe, copied master, ordered native document insertion, source-revision checks, privacy-safe body structure/text evidence, risky-OOXML evidence, and isolated process-group cleanup with separate real subprocess regression coverage. Its first pass rule deliberately does not certify section/page-layout/header/footer/page-number/rendering fidelity.

Microsoft Word has a separate **non-production native multi-document acceptance prototype** using real section boundaries, measured structure/text/section/page-number evidence, source-revision binding, exact Word-process cleanup safeguards, and a dedicated controlled timeout-cleanup harness.

Capability reporting separates local detection/automation readiness from production readiness. LibreOffice and Word remain `production_ready=false`; neither can silently replace portable merge mode.

The LibreOffice UNO workflow runs only on the maintained supervised implementation; the older duplicate native draft was removed. A workflow definition is not proof of a passing external application run.

The controlled Word acceptance workflow is manual-only on a dedicated self-hosted Windows runner with Microsoft Word actually installed. Defining that workflow does not constitute a passing Word run. Real normal-operation and forced-timeout Word evidence, representative private corpora, and human rendering review remain required before any production Word claim.

See [DOCX Engine](docs/docx-engine.md), [DOCX Fidelity Adapters and Acceptance](docs/docx-fidelity-acceptance.md), [LibreOffice Native Multi-Document Merge Acceptance](docs/libreoffice-native-merge-acceptance.md), [Microsoft Word Native Merge Acceptance](docs/word-native-merge-acceptance.md), [Microsoft Word Timeout Cleanup Acceptance](docs/word-timeout-cleanup-acceptance.md), [Private DOCX Fidelity Corpus Testing](docs/docx-fidelity-corpus.md), and [Known Limitations](docs/known-limitations.md).

## Repository structure

```text
src/docmergeforge/    application source
tests/                unit, integration, regression
scripts/              build, fixture, stress, accessibility, acceptance tools
docs/                 complete user/operator/developer documentation
assets/branding/      original SVG branding
.github/workflows/    quality, regression, build, security, package, stress, fidelity automation
```

Architecture details: [docs/architecture.md](docs/architecture.md). File-by-file ownership and purpose: [docs/repository-reference.md](docs/repository-reference.md).

## Quality commands

```bash
pre-commit validate-config
ruff check .
black --check --diff .
mypy src/docmergeforge
python scripts/check_docs_links.py
python scripts/check_repository_reference.py
pytest
```

The repository-reference checker uses the tracked `git ls-files` set and requires every tracked path to be explicitly cataloged in `docs/repository-reference.md`, preventing new source/tests/workflows/config/assets/docs from silently becoming undocumented.

CI also exercises the responsive web/API merge tests, generated 120-part regression, cross-platform desktop build/accessibility smoke, CodeQL security analysis, package building, a real LibreOffice one-document fidelity lane, supervised real Writer multi-document insertion and process cleanup lanes, and a manual controlled Microsoft Word native acceptance workflow.

See [Testing and CI](docs/testing-and-ci.md) and [Automation and Workflow Reference](docs/automation-reference.md).

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

Native desktop/CLI document processing is local-first and does not require a DocMergeForge account or upload manuscripts to a DocMergeForge-operated cloud service. Browser mode adds a browser-to-Python-host network boundary: selected manuscript bytes and any shared PDF password travel to the host you chose.

The built-in web host defaults to loopback. Non-loopback binds require an access token, and the browser token is entered in a masked field or handled through a `#token=...` fragment rather than a query parameter. Token authentication does not encrypt traffic, so use HTTPS plus appropriate reverse-proxy/authentication hardening when traffic leaves a trusted local environment.

Passwords are not persisted to project files, diagnostics are designed to exclude manuscript body text/passwords, companion archives are not auto-extracted, and private fidelity corpus execution does not upload source documents to a project-operated service.

Common private corpus/evidence directories plus local transaction state are ignored by default, but `.gitignore` is only a safety net. Review every staged file before committing or uploading artifacts.

Fidelity corpus reports replace corpus/output roots with relative/placeheld paths, but generated DOCX copies, hashes, filenames, process/environment evidence, host logs, and third-party office errors can still be sensitive and should be reviewed before sharing.

Review paths/filenames in project files, project-sync previews, reports, manifests, diagnostics, audit output, browser-host logs, and fidelity evidence before sharing them publicly.

- [Privacy](docs/privacy.md)
- [Security Model](docs/security.md)
- [Platform Support](docs/platform-support.md)
- [Security reporting policy](SECURITY.md)
- [Diagnostics and Logging](docs/diagnostics.md)

## Accessibility

Important desktop controls expose explicit accessible metadata and keyboard behavior, with an offscreen accessibility smoke exercised in cross-platform Build Smoke.

The responsive browser shell uses semantic labels/status output and mobile-friendly controls, but automated host/API tests are not represented as complete assistive-technology acceptance across mobile/desktop browsers.

Automated metadata checks are not represented as full human accessibility certification; screen-reader/high-contrast/scaling/reduced-motion acceptance remains part of the stable-release gate.

See [Accessibility](docs/accessibility.md).

## Release status

DocMergeForge remains pre-stable. Green source CI and unsigned PyInstaller archives do not by themselves justify a `v1.0.0` production-ready claim.

Open acceptance areas include representative Android/iOS/iPadOS/ChromeOS/desktop-browser acceptance for the responsive client, measured multi-gigabyte stress, representative real-world fidelity, reviewed supervised LibreOffice UNO multi-document/process-cleanup runs plus broader section/page-layout fidelity before LibreOffice native mode is claimed, controlled Microsoft Word normal/forced-timeout/corpus/manual acceptance before Word native mode is claimed, human accessibility, clean-machine interactive packaged-app acceptance, additional physical/filesystem/network failure modes where claimed, and platform signing/notarization where distributed.

Controlled abrupt-process recovery and Linux real-`ENOSPC` acceptance already have recorded evidence; they are not reused as proof for the separate open environments above.

See [Release Process](docs/release-process.md), [Known Limitations](docs/known-limitations.md), [Release Evidence Ledger](docs/release-evidence.md), and [what_changed.md](what_changed.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [Development Guide](docs/development.md), [Test Suite Reference](docs/test-suite-reference.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). GitHub issue/PR templates require privacy-safe reproductions and explicit validation/evidence boundaries for document-engine, recovery, packaging, and fidelity changes.

## License

MIT — see [LICENSE](LICENSE).

## Support and creator

- Repository: https://github.com/sanskarIN/DocMergeForge
- GitHub: https://www.github.com/sanskarIN
- LinkedIn: https://www.linkedin.com/in/sanskarIN
- **Buy Me a Coffee:** https://buymeacoffee.com/sanskarIN
- YouTube: https://youtube.com/@Sanskar-in
- X: https://x.com/x_sanskarIN
- Business: `sanskarin@outlook.in`
- Business: `sanskarin.business@gmail.com`
- Support: `supportramsandesh@gmail.com`