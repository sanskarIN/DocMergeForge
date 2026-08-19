import errno
from pathlib import Path

import pytest

import docmergeforge.utilities.output_lock as output_lock
from docmergeforge.core.exceptions import OutputLockError
from docmergeforge.utilities.output_lock import LOCK_FILENAME, OutputDirectoryLock


def test_output_directory_lock_is_exclusive(tmp_path: Path) -> None:
    first = OutputDirectoryLock(tmp_path)
    second = OutputDirectoryLock(tmp_path)

    first.acquire()
    try:
        assert first.acquired
        with pytest.raises(OutputLockError, match="already using this output directory"):
            second.acquire()
        assert not second.acquired
    finally:
        first.release()


def test_output_directory_lock_can_be_reacquired_after_release(tmp_path: Path) -> None:
    with OutputDirectoryLock(tmp_path):
        assert (tmp_path / LOCK_FILENAME).is_file()

    with OutputDirectoryLock(tmp_path) as lock:
        assert lock.acquired

    assert not lock.acquired


def test_output_directory_lock_release_is_idempotent(tmp_path: Path) -> None:
    lock = OutputDirectoryLock(tmp_path)
    lock.acquire()
    lock.release()
    lock.release()

    assert not lock.acquired


def test_output_directory_lock_refuses_symlink_lock_file(tmp_path: Path) -> None:
    victim = tmp_path / "victim.bin"
    victim.write_bytes(b"")
    lock_path = tmp_path / LOCK_FILENAME
    try:
        lock_path.symlink_to(victim)
    except OSError as exc:
        pytest.skip(f"File symlinks are unavailable: {exc}")

    with pytest.raises(OutputLockError, match="symlink"):
        OutputDirectoryLock(tmp_path).acquire()

    assert victim.read_bytes() == b""


def test_output_directory_lock_reports_lock_file_open_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_open(path: Path, flags: int, mode: int) -> int:
        del path, flags, mode
        raise PermissionError(errno.EACCES, "simulated lock-file denial")

    monkeypatch.setattr(output_lock.os, "open", failing_open)

    with pytest.raises(OutputLockError, match="Could not open output-directory lock file"):
        OutputDirectoryLock(tmp_path).acquire()
