from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
_SKIP_DIRECTORIES = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "build", "dist"}


@dataclass(slots=True, frozen=True)
class BrokenLink:
    source: Path
    target: str
    resolved: Path


def _markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if not any(part in _SKIP_DIRECTORIES for part in path.relative_to(root).parts)
    )


def _local_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if not target or target.startswith("#"):
        return None

    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None

    path = unquote(parsed.path)
    return path or None


def find_broken_links(root: Path) -> list[BrokenLink]:
    """Return broken repository-local Markdown links below ``root``."""

    root = root.resolve()
    broken: list[BrokenLink] = []
    for source in _markdown_files(root):
        text = source.read_text(encoding="utf-8")
        for match in _LINK_PATTERN.finditer(text):
            raw_target = match.group(1)
            local = _local_target(raw_target)
            if local is None:
                continue
            resolved = (source.parent / local).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                broken.append(BrokenLink(source, raw_target, resolved))
                continue
            if not resolved.exists():
                broken.append(BrokenLink(source, raw_target, resolved))
    return broken
