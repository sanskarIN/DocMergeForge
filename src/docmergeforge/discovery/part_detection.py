from __future__ import annotations

import re
from pathlib import Path

from docmergeforge.core.models import PartIdentity

_PART_PATTERNS = [
    re.compile(r"(?i)\b(?:part|chapter|volume)[ _.-]*0*(\d{1,6})\b"),
    re.compile(r"(?i)(?:^|[_ .-])p(?:art)?[_ .-]*0*(\d{1,6})(?:[_ .-]|$)"),
]


def detect_part(path: Path) -> PartIdentity:
    stem = path.stem
    for pattern in _PART_PATTERNS:
        match = pattern.search(stem)
        if match:
            number = int(match.group(1))
            return PartIdentity(number=number, label=f"Part {number}", title=_clean_title(stem))
    return PartIdentity(number=None, label=stem, title=_clean_title(stem))


def _clean_title(stem: str) -> str:
    text = re.sub(r"[_-]+", " ", stem)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def natural_key(value: str | Path) -> tuple[object, ...]:
    text = str(value).casefold()
    return tuple(int(token) if token.isdigit() else token for token in re.split(r"(\d+)", text))


def sort_documents_naturally(paths: list[Path]) -> list[Path]:
    return sorted(paths, key=lambda p: natural_key(p.name))
