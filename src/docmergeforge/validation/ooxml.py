from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docmergeforge.core.models import Diagnostic, DiagnosticLevel

_REQUIRED = {"[Content_Types].xml", "word/document.xml", "_rels/.rels"}


def validate_docx_package(path: Path) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if not zipfile.is_zipfile(path):
        return [
            Diagnostic(
                DiagnosticLevel.ERROR,
                "DOCX is not a valid ZIP/OOXML container.",
                path,
                "Replace or repair this DOCX before merging.",
            )
        ]

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        for required in sorted(_REQUIRED - names):
            diagnostics.append(
                Diagnostic(
                    DiagnosticLevel.ERROR,
                    f"Required OOXML member is missing: {required}",
                    path,
                    "Repair or re-save the document in Microsoft Word or LibreOffice.",
                )
            )
        for name in ("word/document.xml", "[Content_Types].xml"):
            if name in names:
                try:
                    ET.fromstring(archive.read(name))
                except ET.ParseError as exc:
                    diagnostics.append(
                        Diagnostic(
                            DiagnosticLevel.ERROR,
                            f"Malformed XML in {name}.",
                            path,
                            "Repair the document before merging.",
                            str(exc),
                        )
                    )
    return diagnostics


def risky_docx_constructs(path: Path) -> list[str]:
    risks: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if any(name.endswith("vbaProject.bin") for name in names):
            risks.append("Macros/VBA project detected.")
        if any("embeddings/" in name for name in names):
            risks.append("Embedded OLE/package objects detected.")
        if "customXml/" in " ".join(names):
            risks.append("Custom XML parts detected.")
        external = [
            name
            for name in names
            if name.endswith(".rels")
            and b'TargetMode="External"' in archive.read(name)
        ]
        if external:
            risks.append("External relationships detected.")
    return risks
