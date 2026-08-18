from __future__ import annotations

import hashlib
import zipfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

from docmergeforge.core.exceptions import ValidationError

_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_SECT_PR = f"{{{_W_NS}}}sectPr"
_PG_NUM_TYPE = f"{{{_W_NS}}}pgNumType"
_W_VAL = f"{{{_W_NS}}}val"
_W_START = f"{{{_W_NS}}}start"
_W_FMT = f"{{{_W_NS}}}fmt"
_W_CHAP_STYLE = f"{{{_W_NS}}}chapStyle"
_W_CHAP_SEP = f"{{{_W_NS}}}chapSep"
_DOCUMENT_XML = "word/document.xml"


@dataclass(slots=True, frozen=True)
class PageNumberSectionRecord:
    start: str
    format: str
    chapter_style: str
    chapter_separator: str

    def canonical(self) -> str:
        return "|".join(
            (
                f"start={self.start}",
                f"format={self.format}",
                f"chapter_style={self.chapter_style}",
                f"chapter_separator={self.chapter_separator}",
            )
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "start": self.start,
            "format": self.format,
            "chapter_style": self.chapter_style,
            "chapter_separator": self.chapter_separator,
        }


def _attribute(element: ElementTree.Element | None, name: str) -> str:
    if element is None:
        return ""
    return element.attrib.get(name, "")


def page_number_section_records(path: Path) -> tuple[PageNumberSectionRecord, ...]:
    """Return ordered page-number properties for every DOCX section.

    The parser reads only `word/document.xml`; it does not render, repair, or mutate the
    package. Sections without an explicit `w:pgNumType` are represented by an empty record
    so section order/count remains part of the evidence.
    """
    if path.suffix.casefold() != ".docx":
        raise ValidationError(f"Page-number evidence requires a DOCX file: {path}")
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)

    try:
        with zipfile.ZipFile(path, "r") as archive:
            try:
                document_xml = archive.read(_DOCUMENT_XML)
            except KeyError as exc:
                raise ValidationError(
                    f"DOCX package is missing {_DOCUMENT_XML}: {path}"
                ) from exc
    except zipfile.BadZipFile as exc:
        raise ValidationError(f"Invalid DOCX ZIP container: {path}") from exc

    try:
        root = ElementTree.fromstring(document_xml)
    except ElementTree.ParseError as exc:
        raise ValidationError(f"Invalid DOCX document XML: {path}") from exc

    records: list[PageNumberSectionRecord] = []
    for section in root.iter(_SECT_PR):
        page_number = section.find(_PG_NUM_TYPE)
        records.append(
            PageNumberSectionRecord(
                start=_attribute(page_number, _W_START),
                format=_attribute(page_number, _W_FMT),
                chapter_style=_attribute(page_number, _W_CHAP_STYLE),
                chapter_separator=_attribute(page_number, _W_CHAP_SEP),
            )
        )

    if not records:
        raise ValidationError(f"DOCX document contains no section properties: {path}")
    return tuple(records)


def _digest_records(records: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for record in records:
        encoded = record.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, byteorder="big", signed=False))
        digest.update(encoded)
    return digest.hexdigest()


def page_number_properties_sha256(paths: Sequence[Path]) -> str:
    """Fingerprint ordered page-number section properties across source documents."""
    if not paths:
        raise ValidationError("Page-number evidence requires at least one DOCX source.")

    canonical_records: list[str] = []
    for document_index, path in enumerate(paths):
        for section_index, record in enumerate(page_number_section_records(path)):
            canonical_records.append(
                f"document={document_index}|section={section_index}|{record.canonical()}"
            )
    return _digest_records(canonical_records)
