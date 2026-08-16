from __future__ import annotations

import posixpath
import zipfile
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET

from docmergeforge.core.models import Diagnostic, DiagnosticLevel

_REQUIRED = {"[Content_Types].xml", "word/document.xml", "_rels/.rels"}
_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _relationship_source(rels_path: str) -> str:
    if rels_path == "_rels/.rels":
        return ""
    directory, filename = posixpath.split(rels_path)
    if not directory.endswith("/_rels"):
        return ""
    source_directory = directory[: -len("/_rels")]
    if not filename.endswith(".rels"):
        return ""
    source_name = filename[: -len(".rels")]
    return posixpath.join(source_directory, source_name)


def _resolve_target(rels_path: str, target: str) -> str:
    target = unquote(target.split("#", 1)[0])
    if target.startswith("/"):
        return target.lstrip("/")
    source = _relationship_source(rels_path)
    base = posixpath.dirname(source)
    return posixpath.normpath(posixpath.join(base, target)).lstrip("./")


def _relationship_diagnostics(path: Path, archive: zipfile.ZipFile) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    names = set(archive.namelist())
    rels_files = sorted(name for name in names if name.endswith(".rels"))

    for rels_path in rels_files:
        try:
            root = ET.fromstring(archive.read(rels_path))
        except ET.ParseError as exc:
            diagnostics.append(
                Diagnostic(
                    DiagnosticLevel.ERROR,
                    f"Malformed relationships XML: {rels_path}",
                    path,
                    "Repair or re-save the DOCX before merging.",
                    str(exc),
                )
            )
            continue

        seen_ids: set[str] = set()
        for relationship in root.findall(f"{{{_REL_NS}}}Relationship"):
            rel_id = relationship.attrib.get("Id", "")
            target = relationship.attrib.get("Target", "")
            target_mode = relationship.attrib.get("TargetMode", "Internal")

            if not rel_id:
                diagnostics.append(
                    Diagnostic(
                        DiagnosticLevel.ERROR,
                        f"Relationship without an Id in {rels_path}.",
                        path,
                        "Repair or re-save the DOCX before merging.",
                    )
                )
            elif rel_id in seen_ids:
                diagnostics.append(
                    Diagnostic(
                        DiagnosticLevel.ERROR,
                        f"Duplicate relationship Id {rel_id} in {rels_path}.",
                        path,
                        "Repair or re-save the DOCX before merging.",
                    )
                )
            seen_ids.add(rel_id)

            if target_mode.casefold() == "external":
                continue
            if not target:
                diagnostics.append(
                    Diagnostic(
                        DiagnosticLevel.ERROR,
                        f"Relationship {rel_id or '<unknown>'} has an empty target in {rels_path}.",
                        path,
                        "Repair or re-save the DOCX before merging.",
                    )
                )
                continue

            resolved = _resolve_target(rels_path, target)
            if resolved and resolved not in names:
                diagnostics.append(
                    Diagnostic(
                        DiagnosticLevel.ERROR,
                        f"Unresolved relationship target: {resolved}",
                        path,
                        "Restore the missing OOXML part or re-save the document.",
                        f"Relationship file: {rels_path}; Id: {rel_id}; Target: {target}",
                    )
                )

    return diagnostics


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
        diagnostics.extend(_relationship_diagnostics(path, archive))
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
            if name.endswith(".rels") and b'TargetMode="External"' in archive.read(name)
        ]
        if external:
            risks.append("External relationships detected.")
    return risks
