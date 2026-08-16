from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def versioned_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    index = 2
    while True:
        candidate = path.with_name(f"{stem}_v{index}{suffix}")
        if not candidate.exists():
            return candidate
        index += 1


@contextmanager
def atomic_output(final_path: Path, overwrite: bool = False) -> Iterator[Path]:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    if final_path.exists() and not overwrite:
        final_path = versioned_path(final_path)

    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{final_path.stem}.",
        suffix=f"{final_path.suffix}.part",
        dir=final_path.parent,
    )
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        yield tmp_path
        if not tmp_path.exists() or tmp_path.stat().st_size == 0:
            raise RuntimeError("Temporary output is missing or empty.")
        os.replace(tmp_path, final_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
