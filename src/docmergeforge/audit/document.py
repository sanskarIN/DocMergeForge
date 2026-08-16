from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docmergeforge.audit.publication import AuditFinding, audit_text

_W_TEXT = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"


def _docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    return "\n".join(node.text or "" for node in root.iter(_W_TEXT))


def audit_document(path: Path) -> list[AuditFinding]:
    suffix = path.suffix.casefold()
    if suffix == ".docx":
        return audit_text(path, _docx_text(path))
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path), strict=False)
        if reader.is_encrypted:
            return [
                AuditFinding(
                    "encrypted-pdf",
                    "Encrypted PDF content was not audited.",
                    path,
                    "WARNING",
                )
            ]
        findings: list[AuditFinding] = []
        for page in reader.pages:
            findings.extend(audit_text(path, page.extract_text() or ""))
        return _deduplicate(findings)
    return []


def _deduplicate(findings: list[AuditFinding]) -> list[AuditFinding]:
    seen: set[tuple[str, str, Path]] = set()
    unique: list[AuditFinding] = []
    for finding in findings:
        key = (finding.code, finding.message, finding.path)
        if key not in seen:
            unique.append(finding)
            seen.add(key)
    return unique


def audit_tree(root: Path) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    paths = [root] if root.is_file() else sorted(root.rglob("*"))
    for path in paths:
        if path.is_file() and path.suffix.casefold() in {".pdf", ".docx"}:
            findings.extend(audit_document(path))
    return findings
