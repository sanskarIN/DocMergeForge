from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docx import Document

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx.fidelity import require_fidelity_automation
from docmergeforge.docx.libreoffice_merge import (
    find_uno_python,
    libreoffice_merge_documents,
)
from docmergeforge.docx.native import (
    validate_native_docx_output,
    verify_native_source_unchanged,
)
from docmergeforge.utilities.hashing import sha256_file
from docmergeforge.validation.ooxml import risky_docx_constructs


@dataclass(slots=True, frozen=True)
class LibreOfficeMergeStructureSnapshot:
    paragraphs: int
    tables: int
    inline_shapes: int
    headings: int

    def to_dict(self) -> dict[str, int]:
        return {
            "paragraphs": self.paragraphs,
            "tables": self.tables,
            "inline_shapes": self.inline_shapes,
            "headings": self.headings,
        }


@dataclass(slots=True, frozen=True)
class LibreOfficeMergeContentSnapshot:
    body_paragraphs_sha256: str
    tables_sha256: str

    def to_dict(self) -> dict[str, str]:
        return {
            "body_paragraphs_sha256": self.body_paragraphs_sha256,
            "tables_sha256": self.tables_sha256,
        }


@dataclass(slots=True, frozen=True)
class LibreOfficeMergeAcceptanceEvidence:
    source_count: int
    source_sha256: tuple[str, ...]
    output: Path
    output_sha256: str
    expected_structure: LibreOfficeMergeStructureSnapshot
    output_structure: LibreOfficeMergeStructureSnapshot
    expected_content: LibreOfficeMergeContentSnapshot
    output_content: LibreOfficeMergeContentSnapshot
    source_risks: tuple[str, ...]
    output_risks: tuple[str, ...]
    new_risks: tuple[str, ...]
    structure_matches: bool
    content_matches: bool

    @property
    def accepted(self) -> bool:
        return self.structure_matches and self.content_matches and not self.new_risks

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_count": self.source_count,
            "source_sha256": list(self.source_sha256),
            "output": str(self.output),
            "output_sha256": self.output_sha256,
            "expected_structure": self.expected_structure.to_dict(),
            "output_structure": self.output_structure.to_dict(),
            "expected_content": self.expected_content.to_dict(),
            "output_content": self.output_content.to_dict(),
            "source_risks": list(self.source_risks),
            "output_risks": list(self.output_risks),
            "new_risks": list(self.new_risks),
            "structure_matches": self.structure_matches,
            "content_matches": self.content_matches,
            "accepted": self.accepted,
        }


def _digest_texts(values: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, byteorder="big", signed=False))
        digest.update(encoded)
    return digest.hexdigest()


def _paragraph_texts(document: Any) -> list[str]:
    return [paragraph.text for paragraph in document.paragraphs if paragraph.text]


def _table_texts(document: Any) -> list[str]:
    values: list[str] = []
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                values.append(cell.text)
    return values


def _heading_count(document: Any) -> int:
    return sum(
        1
        for paragraph in document.paragraphs
        if paragraph.style and paragraph.style.name.startswith("Heading")
    )


def snapshot_libreoffice_merge_structure(path: Path) -> LibreOfficeMergeStructureSnapshot:
    document = Document(str(path))
    return LibreOfficeMergeStructureSnapshot(
        paragraphs=len(_paragraph_texts(document)),
        tables=len(document.tables),
        inline_shapes=len(document.inline_shapes),
        headings=_heading_count(document),
    )


def snapshot_libreoffice_merge_content(path: Path) -> LibreOfficeMergeContentSnapshot:
    document = Document(str(path))
    return LibreOfficeMergeContentSnapshot(
        body_paragraphs_sha256=_digest_texts(_paragraph_texts(document)),
        tables_sha256=_digest_texts(_table_texts(document)),
    )


def expected_libreoffice_merge_structure(
    sources: Sequence[Path],
) -> LibreOfficeMergeStructureSnapshot:
    if not sources:
        raise ValidationError("LibreOffice merge acceptance requires at least one DOCX source.")
    snapshots = [snapshot_libreoffice_merge_structure(path) for path in sources]
    return LibreOfficeMergeStructureSnapshot(
        paragraphs=sum(item.paragraphs for item in snapshots),
        tables=sum(item.tables for item in snapshots),
        inline_shapes=sum(item.inline_shapes for item in snapshots),
        headings=sum(item.headings for item in snapshots),
    )


def expected_libreoffice_merge_content(
    sources: Sequence[Path],
) -> LibreOfficeMergeContentSnapshot:
    if not sources:
        raise ValidationError("LibreOffice merge acceptance requires at least one DOCX source.")
    paragraphs: list[str] = []
    tables: list[str] = []
    for source in sources:
        document = Document(str(source))
        paragraphs.extend(_paragraph_texts(document))
        tables.extend(_table_texts(document))
    return LibreOfficeMergeContentSnapshot(
        body_paragraphs_sha256=_digest_texts(paragraphs),
        tables_sha256=_digest_texts(tables),
    )


def _validate_acceptance_inputs(
    sources: Sequence[Path], output: Path, timeout_seconds: int
) -> tuple[Path, ...]:
    ordered = tuple(Path(source) for source in sources)
    if not ordered:
        raise ValidationError("LibreOffice merge acceptance requires at least one DOCX source.")
    if output.suffix.casefold() != ".docx":
        raise ValidationError("LibreOffice merge acceptance output must use .docx.")
    if timeout_seconds < 1:
        raise ValidationError("LibreOffice merge acceptance timeout must be at least one second.")

    output_resolved = output.resolve()
    resolved_sources: set[Path] = set()
    for source in ordered:
        if source.suffix.casefold() != ".docx":
            raise ValidationError(
                f"LibreOffice merge acceptance accepts DOCX files only: {source}"
            )
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(source)
        resolved = source.resolve()
        if resolved == output_resolved:
            raise ValidationError(
                "LibreOffice merge acceptance requires a separate output path."
            )
        if resolved in resolved_sources:
            raise ValidationError(f"Duplicate LibreOffice acceptance source: {source}")
        resolved_sources.add(resolved)
        validate_native_docx_output(source)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing DOCX output: {output}")
    return ordered


def _verify_source_hashes(sources: Sequence[Path], hashes: Sequence[str]) -> None:
    for source, expected_hash in zip(sources, hashes, strict=True):
        verify_native_source_unchanged(source, expected_hash)


def run_libreoffice_merge_acceptance(
    sources: Sequence[Path],
    output: Path,
    *,
    timeout_seconds: int = 300,
    start_each_on_new_page: bool = True,
) -> LibreOfficeMergeAcceptanceEvidence:
    """Run the POSIX LibreOffice UNO prototype and return measured evidence.

    The current acceptance scope intentionally covers body structure/text and newly
    introduced risky OOXML categories. Section/page-layout equivalence remains a separate
    certification gate.
    """
    ordered_sources = _validate_acceptance_inputs(sources, output, timeout_seconds)
    source_hashes = tuple(sha256_file(source) for source in ordered_sources)
    expected_structure = expected_libreoffice_merge_structure(ordered_sources)
    expected_content = expected_libreoffice_merge_content(ordered_sources)
    source_risks = tuple(
        sorted({risk for source in ordered_sources for risk in risky_docx_constructs(source)})
    )
    _verify_source_hashes(ordered_sources, source_hashes)

    capability = require_fidelity_automation("libreoffice")
    uno_python = find_uno_python()
    if uno_python is None:
        raise ValidationError(
            "LibreOffice multi-document acceptance requires a Python UNO bridge."
        )
    libreoffice_merge_documents(
        ordered_sources,
        output,
        executable=capability.executable,
        uno_python=uno_python,
        timeout_seconds=timeout_seconds,
        start_each_on_new_page=start_each_on_new_page,
    )
    _verify_source_hashes(ordered_sources, source_hashes)

    output_structure = snapshot_libreoffice_merge_structure(output)
    output_content = snapshot_libreoffice_merge_content(output)
    output_risks = tuple(risky_docx_constructs(output))
    new_risks = tuple(sorted(set(output_risks) - set(source_risks)))
    _verify_source_hashes(ordered_sources, source_hashes)

    return LibreOfficeMergeAcceptanceEvidence(
        source_count=len(ordered_sources),
        source_sha256=source_hashes,
        output=output,
        output_sha256=sha256_file(output),
        expected_structure=expected_structure,
        output_structure=output_structure,
        expected_content=expected_content,
        output_content=output_content,
        source_risks=source_risks,
        output_risks=output_risks,
        new_risks=new_risks,
        structure_matches=expected_structure == output_structure,
        content_matches=expected_content == output_content,
    )
