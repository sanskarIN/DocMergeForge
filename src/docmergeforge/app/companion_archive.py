from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from docmergeforge.companion.organizer import CompanionCopyResult, copy_companion_packages
from docmergeforge.core.models import CompanionReference, DocumentKind
from docmergeforge.discovery.scanner import scan
from docmergeforge.reports.generator import write_companion_index


@dataclass(slots=True, frozen=True)
class CompanionArchiveResult:
    destination: Path
    packages: list[CompanionCopyResult]
    markdown_index: Path
    json_index: Path


def create_copy_only_companion_archive(
    source_roots: list[Path],
    destination: Path,
) -> CompanionArchiveResult:
    """Copy package files unchanged into an organized archive without extraction."""
    discovered = scan(source_roots, recursive=True)
    companions = [item for item in discovered if item.kind == DocumentKind.COMPANION]
    references = [
        CompanionReference(
            part=item.part.number,
            path=item.path,
            sha256=item.sha256,
            size=item.size,
        )
        for item in companions
    ]
    if not references:
        raise ValueError("No companion package files were discovered.")

    destination.mkdir(parents=True, exist_ok=True)
    copied = copy_companion_packages(references, destination)
    markdown_index = destination / "Companion_Code_Index.md"
    json_index = destination / "Companion_Code_Index.json"
    write_companion_index(references, markdown_index, json_index)
    return CompanionArchiveResult(
        destination=destination,
        packages=copied,
        markdown_index=markdown_index,
        json_index=json_index,
    )
