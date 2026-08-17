from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _existing_anchor(path: Path) -> Path:
    current = path.resolve()
    while not current.exists():
        parent = current.parent
        if parent == current:
            raise FileNotFoundError(f"Could not find an existing parent for {path}")
        current = parent
    return current


def _disk_free_bytes(path: Path) -> int:
    return shutil.disk_usage(_existing_anchor(path)).free


def _max_rss_bytes(ru_maxrss: float) -> int:
    # Linux/BSD report KiB; macOS reports bytes.
    if sys.platform == "darwin":
        return int(ru_maxrss)
    return int(ru_maxrss * 1024)


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def run_measured(command: list[str], *, evidence_path: Path, watch_path: Path) -> int:
    if not command:
        raise ValueError("A command is required after --")

    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    disk_free_before = _disk_free_bytes(watch_path)
    started_at = datetime.now(UTC)
    started = time.perf_counter()

    completed = subprocess.run(command, check=False)

    elapsed = time.perf_counter() - started
    finished_at = datetime.now(UTC)
    disk_free_after = _disk_free_bytes(watch_path)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)

    payload: dict[str, Any] = {
        "schema_version": 1,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "platform": platform.system(),
        "architecture": platform.machine(),
        "command_executable": Path(command[0]).name,
        "argument_count": len(command) - 1,
        "exit_code": completed.returncode,
        "elapsed_seconds": elapsed,
        "user_cpu_seconds": max(0.0, after.ru_utime - before.ru_utime),
        "system_cpu_seconds": max(0.0, after.ru_stime - before.ru_stime),
        "max_rss_bytes": _max_rss_bytes(after.ru_maxrss),
        "minor_page_faults": max(0, after.ru_minflt - before.ru_minflt),
        "major_page_faults": max(0, after.ru_majflt - before.ru_majflt),
        "filesystem_input_blocks": max(0, after.ru_inblock - before.ru_inblock),
        "filesystem_output_blocks": max(0, after.ru_oublock - before.ru_oublock),
        "disk_free_before_bytes": disk_free_before,
        "disk_free_after_bytes": disk_free_after,
    }
    _atomic_write_json(evidence_path, payload)
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a command and write privacy-safe resource evidence."
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--watch-path", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("a command is required after --")

    return run_measured(
        command,
        evidence_path=args.output,
        watch_path=args.watch_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
