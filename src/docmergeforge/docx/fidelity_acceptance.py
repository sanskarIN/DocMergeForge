from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx.fidelity import require_fidelity_automation
from docmergeforge.docx.libreoffice import libreoffice_roundtrip_copy
from docmergeforge.docx.word import word_roundtrip_copy
from docmergeforge.utilities.hashing import sha256_file
from docmergeforge.validation.ooxml import risky_docx_constructs, validate_docx_package


@dataclass(slots=True, frozen=True)
class DocxStructureSnapshot:
    paragraphs: int
    tables: int
    inline_shapes: int
    sections: int
    headings: int
    header_paragraphs: int = 0
    footer_paragraphs: int = 0
    header_tables: int = 0
    footer_tables: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "paragraphs": self.paragraphs,
            "tables": self.tables,
            "inline_shapes": self.inline_shapes,
            "sections": self.sections,
            "headings": self.headings,
            "header_paragraphs": self.header_paragraphs,
            "footer_paragraphs": self.footer_paragraphs,
            "header_tables": self.header_tables,
            "footer_tables": self.footer_tables,
        }


@dataclass(slots=True, frozen=True)
class DocxContentSnapshot:
    body_paragraphs_sha256: str
    tables_sha256: str
    headers_sha256: str
    footers_sha256: str

    def to_dict(self) -> dict[str, str]:
        return {
            "body_paragraphs_sha256": self.body_paragraphs_sha256,
            "tables_sha256": self.tables_sha256,
            "headers_sha256": self.headers_sha256,
            "footers_sha256": self.footers_sha256,
        }


@dataclass(slots=True, frozen=True)
class FidelityAcceptanceEvidence:
    mode: str
    source: Path
    output: Path
    source_sha256: str
    output_sha256: str
    source_structure: DocxStructureSnapshot
    output_structure: DocxStructureSnapshot
    source_content: DocxContentSnapshot
    output_content: DocxContentSnapshot
    source_risks: tuple[str, ...]
    output_risks: tuple[str, ...]
    structure_matches: bool
    content_matches: bool
    new_risks: tuple[str, ...]

    @property
    def accepted(self) -> bool:
        return self.structure_matches and self.content_matches and not self.new_risks

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "source": str(self.source),
            "output": str(self.output),
            "source_sha256": self.source_sha256,
            "output_sha256": self.output_sha256,
            "source_structure": self.source_structure.to_dict(),
            "output_structure": self.output_structure.to_dict(),
            "source_content": self.source_content.to_dict(),
            "output_content": self.output_content.to_dict(),
            "source_risks": list(self.source_risks),
            "output_risks": list(self.output_risks),
            "structure_matches": self.structure_matches,
            "content_matches": self.content_matches,
            "new_risks": list(self.new_risks),
            "accepted": self.accepted,
        }


def _digest_texts(values: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, byteorder="big", signed=False))
        digest.update(encoded)
    return digest.hexdigest()


def _table_texts(tables: Iterable[Any]) -> Iterable[str]:
    for table in tables:
        for row in table.rows:
            for cell in row.cells:
                yield cell.text


def snapshot_docx_structure(path: Path) -> DocxStructureSnapshot:
    from docx import Document

    document = Document(str(path))
    headings = sum(
        1
        for paragraph in document.paragraphs
        if paragraph.style and paragraph.style.name.startswith("Heading")
    )
    return DocxStructureSnapshot(
        paragraphs=len(document.paragraphs),
        tables=len(document.tables),
        inline_shapes=len(document.inline_shapes),
        sections=len(document.sections),
        headings=headings,
        header_paragraphs=sum(
            len(section.header.paragraphs) for section in document.sections
        ),
        footer_paragraphs=sum(
            len(section.footer.paragraphs) for section in document.sections
        ),
        header_tables=sum(len(section.header.tables) for section in document.sections),
        footer_tables=sum(len(section.footer.tables) for section in document.sections),
    )


def snapshot_docx_content(path: Path) -> DocxContentSnapshot:
    from docx import Document

    document = Document(str(path))
    header_texts: list[str] = []
    footer_texts: list[str] = []
    for section in document.sections:
        header_texts.extend(paragraph.text for paragraph in section.header.paragraphs)
        header_texts.extend(_table_texts(section.header.tables))
        footer_texts.extend(paragraph.text for paragraph in section.footer.paragraphs)
        footer_texts.extend(_table_texts(section.footer.tables))

    return DocxContentSnapshot(
        body_paragraphs_sha256=_digest_texts(
            paragraph.text for paragraph in document.paragraphs
        ),
        tables_sha256=_digest_texts(_table_texts(document.tables)),
        headers_sha256=_digest_texts(header_texts),
        footers_sha256=_digest_texts(footer_texts),
    )


def _require_valid_docx(path: Path) -> None:
    diagnostics = validate_docx_package(path)
    blocking = [item for item in diagnostics if item.level.value in {"ERROR", "FATAL"}]
    if blocking:
        raise ValidationError(f"DOCX fidelity acceptance input is invalid: {blocking[0].message}")


def run_fidelity_roundtrip_acceptance(
    source: Path,
    output: Path,
    mode: str,
    *,
    timeout_seconds: int = 300,
) -> FidelityAcceptanceEvidence:
    """Run one explicit external-office round-trip and return reviewable evidence.

    Passing this check means the selected file survived the measured structural/content
    checks. It does not mark the adapter production-ready globally; representative corpus
    and platform acceptance remain separate release gates.
    """
    if mode not in {"libreoffice", "word"}:
        raise ValidationError(
            "Fidelity round-trip acceptance requires mode 'libreoffice' or 'word'."
        )
    capability = require_fidelity_automation(mode)
    _require_valid_docx(source)

    source_sha256 = sha256_file(source)
    source_structure = snapshot_docx_structure(source)
    source_content = snapshot_docx_content(source)
    source_risks = tuple(risky_docx_constructs(source))

    if mode == "libreoffice":
        libreoffice_roundtrip_copy(
            source,
            output,
            executable=capability.executable,
            timeout_seconds=timeout_seconds,
        )
    else:
        word_roundtrip_copy(
            source,
            output,
            powershell=capability.executable,
            timeout_seconds=timeout_seconds,
        )

    _require_valid_docx(output)
    output_structure = snapshot_docx_structure(output)
    output_content = snapshot_docx_content(output)
    output_risks = tuple(risky_docx_constructs(output))
    new_risks = tuple(sorted(set(output_risks) - set(source_risks)))

    return FidelityAcceptanceEvidence(
        mode=mode,
        source=source,
        output=output,
        source_sha256=source_sha256,
        output_sha256=sha256_file(output),
        source_structure=source_structure,
        output_structure=output_structure,
        source_content=source_content,
        output_content=output_content,
        source_risks=source_risks,
        output_risks=output_risks,
        structure_matches=source_structure == output_structure,
        content_matches=source_content == output_content,
        new_risks=new_risks,
    )
