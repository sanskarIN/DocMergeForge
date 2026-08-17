from pathlib import Path

import pytest

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
