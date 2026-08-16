from __future__ import annotations

import hashlib
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from docmergeforge.validation.ooxml import risky_docx_constructs

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_W_STYLE = f"{{{_W}}}style"
_W_NAME = f"{{{_W}}}name"
_W_VAL = f"{{{_W}}}val"
_W_STYLE_ID = f"{{{_W}}}styleId"


@dataclass(slots=True, frozen=True)
class DocxInventory:
    path: Path
    paragraphs: int
    headings: int
    tables: int
    media_items: int
    sections: int
    style_names: tuple[str, ...]
    risks: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class PackageCollision:
    category: str
    name: str
    paths: tuple[Path, ...]
    fingerprints: tuple[str, ...]


def _fingerprint(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _style_entries(archive: zipfile.ZipFile) -> dict[str, str]:
    if "word/styles.xml" not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read("word/styles.xml"))
    entries: dict[str, str] = {}
    for style in root.findall(f".//{_W_STYLE}"):
        style_id = style.attrib.get(_W_STYLE_ID, "")
        name_node = style.find(_W_NAME)
        name = name_node.attrib.get(_W_VAL, "") if name_node is not None else ""
        key = name or style_id or "<unnamed>"
        entries[key] = _fingerprint(ET.tostring(style, encoding="utf-8"))
    return entries


def _numbering_entries(archive: zipfile.ZipFile) -> dict[str, str]:
    if "word/numbering.xml" not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read("word/numbering.xml"))
    entries: dict[str, str] = {}
    num_tag = f"{{{_W}}}num"
    num_id = f"{{{_W}}}numId"
    for node in root.findall(f".//{num_tag}"):
        key = node.attrib.get(num_id, "<unknown>")
        entries[key] = _fingerprint(ET.tostring(node, encoding="utf-8"))
    return entries


def analyze_docx(path: Path) -> DocxInventory:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
        paragraphs = len(root.findall(f".//{{{_W}}}p"))
        tables = len(root.findall(f".//{{{_W}}}tbl"))
        sections = len(root.findall(f".//{{{_W}}}sectPr"))
        headings = 0
        for paragraph in root.findall(f".//{{{_W}}}p"):
            style = paragraph.find(f"./{{{_W}}}pPr/{{{_W}}}pStyle")
            if style is not None and style.attrib.get(_W_VAL, "").casefold().startswith("heading"):
                headings += 1
        media_items = sum(1 for name in archive.namelist() if name.startswith("word/media/"))
        style_names = tuple(sorted(_style_entries(archive)))

    return DocxInventory(
        path=path,
        paragraphs=paragraphs,
        headings=headings,
        tables=tables,
        media_items=media_items,
        sections=sections,
        style_names=style_names,
        risks=tuple(risky_docx_constructs(path)),
    )


def _collect_package_entries(
    paths: list[Path],
    extractor: str,
) -> dict[str, list[tuple[Path, str]]]:
    collected: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    for path in paths:
        with zipfile.ZipFile(path) as archive:
            if extractor == "style":
                entries = _style_entries(archive)
            elif extractor == "numbering":
                entries = _numbering_entries(archive)
            else:
                entries = {
                    name: _fingerprint(archive.read(name))
                    for name in archive.namelist()
                    if name.startswith("word/media/")
                }
        for name, fingerprint in entries.items():
            collected[name].append((path, fingerprint))
    return collected


def detect_docx_collisions(paths: list[Path]) -> list[PackageCollision]:
    collisions: list[PackageCollision] = []
    for category in ("style", "numbering", "media"):
        entries = _collect_package_entries(paths, category)
        for name, records in sorted(entries.items()):
            fingerprints = {fingerprint for _, fingerprint in records}
            if len(records) > 1 and len(fingerprints) > 1:
                collisions.append(
                    PackageCollision(
                        category=category,
                        name=name,
                        paths=tuple(path for path, _ in records),
                        fingerprints=tuple(sorted(fingerprints)),
                    )
                )
    return collisions
