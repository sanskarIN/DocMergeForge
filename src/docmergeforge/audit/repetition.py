from __future__ import annotations

import hashlib
import re
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

_W_TEXT = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"


@dataclass(slots=True, frozen=True)
class RepetitionCandidate:
    signature: str
    paths: tuple[Path, ...]
    preview: str
    category: str = "suspected-repeated-front-matter"


def _normalize(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"\bpart\s*\d+\b", "part #", text)
    text = re.sub(r"\bchapter\s*\d+\b", "chapter #", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _signature(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()


def _docx_prefix(path: Path, paragraph_limit: int) -> str:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    texts: list[str] = []
    for paragraph in root.findall(
        ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"
    ):
        value = "".join(node.text or "" for node in paragraph.iter(_W_TEXT)).strip()
        if value:
            texts.append(value)
        if len(texts) >= paragraph_limit:
            break
    return "\n".join(texts)


def _pdf_prefix(path: Path, page_limit: int) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path), strict=False)
    if reader.is_encrypted:
        return ""
    return "\n".join((page.extract_text() or "") for page in reader.pages[:page_limit])


def detect_repeated_front_matter(
    paths: list[Path],
    *,
    docx_paragraph_limit: int = 12,
    pdf_page_limit: int = 2,
    min_normalized_chars: int = 40,
) -> list[RepetitionCandidate]:
    grouped: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    for path in paths:
        suffix = path.suffix.casefold()
        if suffix == ".docx":
            text = _docx_prefix(path, docx_paragraph_limit)
        elif suffix == ".pdf":
            text = _pdf_prefix(path, pdf_page_limit)
        else:
            continue
        normalized = _normalize(text)
        if len(normalized) < min_normalized_chars:
            continue
        grouped[_signature(text)].append((path, text))

    candidates: list[RepetitionCandidate] = []
    for signature, records in grouped.items():
        if len(records) < 2:
            continue
        preview = _normalize(records[0][1])[:240]
        candidates.append(
            RepetitionCandidate(
                signature=signature,
                paths=tuple(path for path, _ in records),
                preview=preview,
            )
        )
    candidates.sort(key=lambda item: (-len(item.paths), item.signature))
    return candidates
