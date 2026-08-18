from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docx import Document

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx.fidelity import require_fidelity_automation
from docmergeforge.docx.native import (
    validate_native_docx_output,
    verify_native_source_unchanged,
)
from docmergeforge.docx.section_evidence import page_number_properties_sha256
from docmergeforge.docx.word_merge import word_merge_documents
from docmergeforge.utilities.hashing import sha256_file
from docmergeforge.validation.ooxml import risky_docx_constructs


@dataclass(slots=True, frozen=True)
class WordMergeStructureSnapshot:
    paragraphs: int
    tables: int
    inline_shapes: int
    headings: int
    sections: int
    header_paragraphs: int
    footer_paragraphs: int
    header_tables: int
    footer_tables: int

    def to_dict(self) -> dict[str, int]:
        return {
            "paragraphs": self.paragraphs,
            "tables": self.tables,
            "inline_shapes": self.inline_shapes,
            "headings": self.headings,
            "sections": self.sections,
            "header_paragraphs": self.header_paragraphs,
            "footer_paragraphs": self.footer_paragraphs,
            "header_tables": self.header_tables,
            "footer_tables": self.footer_tables,
        }


@dataclass(slots=True, frozen=True)
class WordMergeContentSnapshot:
    body_paragraphs_sha256: str
    tables_sha256: str
    headers_sha256: str
    footers_sha256: str
    section_properties_sha256: str
    page_number_properties_sha256: str

    def to_dict(self) -> dict[str, str]:
        return {
            "body_paragraphs_sha256": self.body_paragraphs_sha256,
            "tables_sha256": self.tables_sha256,
            "headers_sha256": self.headers_sha256,
            "footers_sha256": self.footers_sha256,
            "section_properties_sha256": self.section_properties_sha256,
            "page_number_properties_sha256": self.page_number_properties_sha256,
        }


@dataclass(slots=True, frozen=True)
class WordMergeAcceptanceEvidence:
    source_count: int
    source_sha256: tuple[str, ...]
    output: Path
    output_sha256: str
    expected_structure: WordMergeStructureSnapshot
    output_structure: WordMergeStructureSnapshot
    expected_content: WordMergeContentSnapshot
    output_content: WordMergeContentSnapshot
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


def _nonempty_paragraph_texts(document: Any) -> list[str]:
    return [paragraph.text for paragraph in document.paragraphs if paragraph.text]


def _table_texts(tables: Iterable[Any]) -> list[str]:
    values: list[str] = []
    for table in tables:
        for row in table.rows:
            for cell in row.cells:
                values.append(cell.text)
    return values


def _header_texts(document: Any) -> list[str]:
    values: list[str] = []
    for section in document.sections:
        values.extend(
            paragraph.text for paragraph in section.header.paragraphs if paragraph.text
        )
        values.extend(_table_texts(section.header.tables))
    return values


def _footer_texts(document: Any) -> list[str]:
    values: list[str] = []
    for section in document.sections:
        values.extend(
            paragraph.text for paragraph in section.footer.paragraphs if paragraph.text
        )
        values.extend(_table_texts(section.footer.tables))
    return values


def _headings(document: Any) -> int:
    return sum(
        1
        for paragraph in document.paragraphs
        if paragraph.style and paragraph.style.name.startswith("Heading")
    )


def _scalar(value: Any) -> str:
    if value is None:
        return ""
    enum_value = getattr(value, "value", None)
    if enum_value is not None:
        return str(enum_value)
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return str(value)


def _section_record(section: Any) -> str:
    return "|".join(
        (
            f"start_type={_scalar(section.start_type)}",
            f"orientation={_scalar(section.orientation)}",
            f"page_width={_scalar(section.page_width)}",
            f"page_height={_scalar(section.page_height)}",
            f"top_margin={_scalar(section.top_margin)}",
            f"bottom_margin={_scalar(section.bottom_margin)}",
            f"left_margin={_scalar(section.left_margin)}",
            f"right_margin={_scalar(section.right_margin)}",
            f"gutter={_scalar(section.gutter)}",
            f"header_distance={_scalar(section.header_distance)}",
            f"footer_distance={_scalar(section.footer_distance)}",
            "different_first_page="
            f"{int(bool(section.different_first_page_header_footer))}",
            f"header_linked={int(bool(section.header.is_linked_to_previous))}",
            "first_header_linked="
            f"{int(bool(section.first_page_header.is_linked_to_previous))}",
            "even_header_linked="
            f"{int(bool(section.even_page_header.is_linked_to_previous))}",
            f"footer_linked={int(bool(section.footer.is_linked_to_previous))}",
            "first_footer_linked="
            f"{int(bool(section.first_page_footer.is_linked_to_previous))}",
            "even_footer_linked="
            f"{int(bool(section.even_page_footer.is_linked_to_previous))}",
        )
    )


def _section_properties_sha256(paths: Sequence[Path]) -> str:
    if not paths:
        raise ValidationError("Word merge section evidence requires at least one source.")
    records: list[str] = []
    global_section_index = 0
    for path in paths:
        document = Document(str(path))
        for section in document.sections:
            records.append(
                f"section={global_section_index}|{_section_record(section)}"
            )
            global_section_index += 1
    return _digest_texts(records)


def snapshot_word_merge_structure(path: Path) -> WordMergeStructureSnapshot:
    document = Document(str(path))
    return WordMergeStructureSnapshot(
        paragraphs=len(_nonempty_paragraph_texts(document)),
        tables=len(document.tables),
        inline_shapes=len(document.inline_shapes),
        headings=_headings(document),
        sections=len(document.sections),
        header_paragraphs=sum(
            len([paragraph for paragraph in section.header.paragraphs if paragraph.text])
            for section in document.sections
        ),
        footer_paragraphs=sum(
            len([paragraph for paragraph in section.footer.paragraphs if paragraph.text])
            for section in document.sections
        ),
        header_tables=sum(len(section.header.tables) for section in document.sections),
        footer_tables=sum(len(section.footer.tables) for section in document.sections),
    )


def snapshot_word_merge_content(path: Path) -> WordMergeContentSnapshot:
    document = Document(str(path))
    return WordMergeContentSnapshot(
        body_paragraphs_sha256=_digest_texts(_nonempty_paragraph_texts(document)),
        tables_sha256=_digest_texts(_table_texts(document.tables)),
        headers_sha256=_digest_texts(_header_texts(document)),
        footers_sha256=_digest_texts(_footer_texts(document)),
        section_properties_sha256=_section_properties_sha256([path]),
        page_number_properties_sha256=page_number_properties_sha256([path]),
    )


def expected_word_merge_structure(sources: Sequence[Path]) -> WordMergeStructureSnapshot:
    if not sources:
        raise ValidationError("Word merge acceptance requires at least one DOCX source.")
    snapshots = [snapshot_word_merge_structure(path) for path in sources]
    return WordMergeStructureSnapshot(
        paragraphs=sum(item.paragraphs for item in snapshots),
        tables=sum(item.tables for item in snapshots),
        inline_shapes=sum(item.inline_shapes for item in snapshots),
        headings=sum(item.headings for item in snapshots),
        sections=sum(item.sections for item in snapshots),
        header_paragraphs=sum(item.header_paragraphs for item in snapshots),
        footer_paragraphs=sum(item.footer_paragraphs for item in snapshots),
        header_tables=sum(item.header_tables for item in snapshots),
        footer_tables=sum(item.footer_tables for item in snapshots),
    )


def expected_word_merge_content(sources: Sequence[Path]) -> WordMergeContentSnapshot:
    if not sources:
        raise ValidationError("Word merge acceptance requires at least one DOCX source.")
    body: list[str] = []
    tables: list[str] = []
    headers: list[str] = []
    footers: list[str] = []
    for path in sources:
        document = Document(str(path))
        body.extend(_nonempty_paragraph_texts(document))
        tables.extend(_table_texts(document.tables))
        headers.extend(_header_texts(document))
        footers.extend(_footer_texts(document))
    return WordMergeContentSnapshot(
        body_paragraphs_sha256=_digest_texts(body),
        tables_sha256=_digest_texts(tables),
        headers_sha256=_digest_texts(headers),
        footers_sha256=_digest_texts(footers),
        section_properties_sha256=_section_properties_sha256(sources),
        page_number_properties_sha256=page_number_properties_sha256(sources),
    )


def _validate_acceptance_inputs(
    sources: Sequence[Path], output: Path, timeout_seconds: int
) -> tuple[Path, ...]:
    ordered_sources = tuple(Path(path) for path in sources)
    if not ordered_sources:
        raise ValidationError("Word merge acceptance requires at least one DOCX source.")
    if output.suffix.casefold() != ".docx":
        raise ValidationError("Word merge acceptance output must use .docx.")
    if timeout_seconds < 1:
        raise ValidationError("Word merge acceptance timeout must be at least one second.")

    output_resolved = output.resolve()
    resolved_sources: set[Path] = set()
    for source in ordered_sources:
        if source.suffix.casefold() != ".docx":
            raise ValidationError(f"Word merge acceptance accepts DOCX files only: {source}")
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(source)
        resolved = source.resolve()
        if resolved == output_resolved:
            raise ValidationError("Word merge acceptance requires a separate output path.")
        if resolved in resolved_sources:
            raise ValidationError(f"Duplicate Word merge acceptance source: {source}")
        resolved_sources.add(resolved)
        validate_native_docx_output(source)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing DOCX output: {output}")
    return ordered_sources


def _verify_source_hashes(
    sources: Sequence[Path], source_hashes: Sequence[str]
) -> None:
    for source, expected_hash in zip(sources, source_hashes, strict=True):
        verify_native_source_unchanged(source, expected_hash)


def run_word_merge_acceptance(
    sources: Sequence[Path],
    output: Path,
    *,
    timeout_seconds: int = 900,
    start_each_on_new_page: bool = True,
) -> WordMergeAcceptanceEvidence:
    """Execute Word native merge and return privacy-safe measured evidence.

    Passing this function is evidence for the measured source set only and never changes
    the Word fidelity capability to production-ready.
    """
    ordered_sources = _validate_acceptance_inputs(sources, output, timeout_seconds)
    source_hashes = tuple(sha256_file(path) for path in ordered_sources)

    expected_structure = expected_word_merge_structure(ordered_sources)
    expected_content = expected_word_merge_content(ordered_sources)
    source_risks = tuple(
        sorted({risk for path in ordered_sources for risk in risky_docx_constructs(path)})
    )
    _verify_source_hashes(ordered_sources, source_hashes)

    capability = require_fidelity_automation("word")
    word_merge_documents(
        ordered_sources,
        output,
        powershell=capability.executable,
        timeout_seconds=timeout_seconds,
        start_each_on_new_page=start_each_on_new_page,
    )
    _verify_source_hashes(ordered_sources, source_hashes)

    output_structure = snapshot_word_merge_structure(output)
    output_content = snapshot_word_merge_content(output)
    output_risks = tuple(risky_docx_constructs(output))
    new_risks = tuple(sorted(set(output_risks) - set(source_risks)))
    _verify_source_hashes(ordered_sources, source_hashes)

    return WordMergeAcceptanceEvidence(
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
