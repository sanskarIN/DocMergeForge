from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

from docmergeforge.core.models import DocumentKind, InputDocument
from docmergeforge.discovery.part_detection import detect_part
from docmergeforge.utilities.hashing import sha256_file

_COMPANION_SUFFIXES = {".zip", ".7z", ".rar", ".tar", ".gz", ".tgz"}


def classify(path: Path) -> DocumentKind:
    suffix = path.suffix.casefold()
    if suffix == ".pdf":
        return DocumentKind.PDF
    if suffix == ".docx":
        return DocumentKind.DOCX
    if suffix in _COMPANION_SUFFIXES or (
        path.is_dir()
        and any(token in path.name.casefold() for token in ("code", "companion", "project"))
    ):
        return DocumentKind.COMPANION
    return DocumentKind.OTHER


def _resolved(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return path.absolute()


def _is_within(path: Path, directory: Path) -> bool:
    try:
        _resolved(path).relative_to(directory)
    except ValueError:
        return False
    return True


def _is_excluded(path: Path, excluded: tuple[Path, ...]) -> bool:
    return any(_is_within(path, directory) for directory in excluded)


def _iter_directory(
    root: Path,
    recursive: bool,
    excluded: tuple[Path, ...],
) -> Iterable[Path]:
    if not recursive:
        for path in root.glob("*"):
            if not _is_excluded(path, excluded) and path.is_file():
                yield path
        return

    for directory, directory_names, file_names in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        directory_names[:] = [
            name
            for name in directory_names
            if not _is_excluded(directory_path / name, excluded)
        ]
        for name in file_names:
            path = directory_path / name
            if not _is_excluded(path, excluded):
                yield path


def iter_files(
    roots: Iterable[Path],
    recursive: bool = True,
    *,
    exclude_roots: Iterable[Path] = (),
) -> Iterable[Path]:
    excluded = tuple(_resolved(path) for path in exclude_roots)
    for root in roots:
        if _is_excluded(root, excluded):
            continue
        if root.is_file():
            yield root
            continue
        if root.is_dir():
            yield from _iter_directory(root, recursive, excluded)


def _path_identity(path: Path) -> str:
    return os.path.normcase(str(_resolved(path)))


def _pdf_info(path: Path) -> tuple[int | None, bool, list[str]]:
    warnings: list[str] = []
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path), strict=False)
        encrypted = bool(reader.is_encrypted)
        if encrypted:
            return None, True, warnings
        return len(reader.pages), False, warnings
    except Exception as exc:
        warnings.append(f"PDF inspection failed: {exc}")
        return None, False, warnings


def scan(
    roots: Iterable[Path],
    recursive: bool = True,
    *,
    exclude_roots: Iterable[Path] = (),
) -> list[InputDocument]:
    results: list[InputDocument] = []
    seen: set[str] = set()
    for path in iter_files(roots, recursive=recursive, exclude_roots=exclude_roots):
        identity = _path_identity(path)
        if identity in seen:
            continue
        seen.add(identity)

        kind = classify(path)
        page_count: int | None = None
        encrypted = False
        warnings: list[str] = []
        if kind == DocumentKind.PDF:
            page_count, encrypted, warnings = _pdf_info(path)
        elif path.suffix.casefold() == ".doc":
            warnings.append(
                "Legacy .doc detected. It is not mergeable until the user explicitly creates "
                "a separate converted .docx copy; the original is never auto-converted."
            )

        results.append(
            InputDocument(
                path=path,
                kind=kind,
                part=detect_part(path),
                size=path.stat().st_size,
                sha256=sha256_file(path),
                page_count=page_count,
                encrypted=encrypted,
                warnings=warnings,
            )
        )
    return results
