# Architecture

DocMergeForge uses a layered, local-first architecture:

```text
PySide6 UI / CLI
        ↓
Application services
        ↓
Domain models + explicit merge state
        ↓
Discovery / Validation / Reports
        ↓
PDF engine / DOCX engine
        ↓
Filesystem and optional external adapters
```

Core rules are enforced below the UI: sources are read-only inputs, output is written atomically, companion code is classified separately, and final success requires validation.

## Fidelity boundary

PDF processing uses `pypdf`. DOCX composition uses `python-docx` plus `docxcompose`. OOXML can contain features that those libraries cannot reproduce perfectly. Risky package constructs are detected where practical and must be surfaced rather than silently discarded.

Optional Word/LibreOffice high-fidelity adapters can be added without coupling the domain layer to a specific desktop suite.
