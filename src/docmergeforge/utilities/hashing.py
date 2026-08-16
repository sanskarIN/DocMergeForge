from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_hashes(paths: Iterable[Path]) -> dict[Path, str]:
    return {path: sha256_file(path) for path in paths}


def verify_unchanged(before: dict[Path, str]) -> list[Path]:
    return [
        path for path, digest in before.items() if not path.exists() or sha256_file(path) != digest
    ]
