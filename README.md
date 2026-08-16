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

## Core guarantees

- PDF and DOCX pipelines remain separate.
- Natural numeric ordering handles Part 2 before Part 10.
- Original source hashes are verified before and after merging.
- Companion code archives are indexed but never merged, extracted, rewritten, or refactored.
- Outputs are created through temporary files and promoted only after validation.
- No manuscript content is uploaded by default.
- No account is required.

## SQL Full Mastery preset

The dedicated **SQL Full Mastery — 120-Part Master Edition** preset expects Parts 1–120, validates PDF and DOCX sets independently, creates the two master manuscripts, and writes checksums, manifests, reports, a companion-code index, and a publishing checklist.

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

## GUI

```bash
docmergeforge-gui
```

The home screen exposes the SQL preset plus entry points for PDF, DOCX, validation, audit, comparison, recovery, settings, help, and About.

## CLI

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

## 120-part regression fixture

```bash
python scripts/generate_120_fixture.py fixtures/generated/sql-120
docmergeforge validate --input fixtures/generated/sql-120 --parts 1-120
```

Each generated companion ZIP is intentionally independent.

## Validation evidence

PDF validation reopens the result and verifies the exact expected page count. DOCX validation checks the OOXML ZIP container, required members, XML parseability, and parser reopen. The application does not report success merely because a library call returned.

## DOCX fidelity policy

Portable DOCX composition is powerful but cannot prove perfect preservation for every Microsoft Word construct. Macros, OLE objects, tracked changes, complex fields, custom XML, some equations, and external relationships are treated as risky. Keep originals and use a high-fidelity desktop-suite path when required.

## Repository structure

```text
src/docmergeforge/    application source
tests/                unit, integration, regression
scripts/              development and fixture tools
docs/                 architecture and operator documentation
assets/branding/      original SVG branding
.github/workflows/    CI and security automation
```

## Quality commands

```bash
ruff check .
black --check .
mypy src/docmergeforge
pytest
```

## Privacy

See [docs/privacy.md](docs/privacy.md). Documents stay on-device by default, passwords are not persisted, and exported diagnostics omit manuscript body text.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

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

**The PDFs are merged. The DOCX files are merged. The code remains separate.**
