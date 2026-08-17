from __future__ import annotations

import argparse
import errno
import os
import shutil
from pathlib import Path

from docmergeforge.utilities.atomic import atomic_output

MAX_SAFE_FREE_BYTES = 128 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024


def run(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    free_before = shutil.disk_usage(output_dir).free
    if free_before > MAX_SAFE_FREE_BYTES:
        raise RuntimeError(
            "Refusing disk-exhaustion acceptance outside a deliberately small filesystem: "
            f"{free_before} free bytes exceeds the {MAX_SAFE_FREE_BYTES}-byte safety limit."
        )

    target = output_dir / "published.bin"
    previous = b"previous-published-output\n"
    target.write_bytes(previous)

    saw_enospc = False
    try:
        with (
            atomic_output(target, overwrite=True) as temporary,
            temporary.open("wb") as handle,
        ):
            chunk = b"x" * CHUNK_SIZE
            while True:
                handle.write(chunk)
                handle.flush()
                os.fsync(handle.fileno())
    except OSError as exc:
        if exc.errno != errno.ENOSPC:
            raise
        saw_enospc = True

    if not saw_enospc:
        raise RuntimeError("Disk-exhaustion acceptance never observed ENOSPC.")
    if target.read_bytes() != previous:
        raise RuntimeError("Previously published target changed after ENOSPC.")

    residue = list(output_dir.glob(".*.part"))
    if residue:
        raise RuntimeError(f"Atomic temporary residue remains after ENOSPC: {residue}")

    print(
        "Real ENOSPC acceptance passed: previous output preserved and atomic temporary "
        f"files cleaned (filesystem began with {free_before} free bytes)."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fill an intentionally small filesystem and validate atomic ENOSPC recovery."
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    run(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
