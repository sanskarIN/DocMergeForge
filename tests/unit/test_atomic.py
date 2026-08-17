import errno
from pathlib import Path

import pytest

from docmergeforge.utilities.atomic import atomic_output, versioned_path


def test_atomic_output_replaces_only_after_success(tmp_path: Path) -> None:
    target = tmp_path / "out.bin"
    with atomic_output(target) as temp:
        temp.write_bytes(b"ok")
        assert not target.exists()
    assert target.read_bytes() == b"ok"


def test_atomic_output_cleans_failed_temp(tmp_path: Path) -> None:
    target = tmp_path / "out.bin"
    with pytest.raises(RuntimeError), atomic_output(target):
        raise RuntimeError("boom")
    assert not target.exists()


def test_atomic_output_preserves_published_file_on_disk_exhaustion(tmp_path: Path) -> None:
    target = tmp_path / "out.bin"
    target.write_bytes(b"published")

    with pytest.raises(OSError) as error, atomic_output(target, overwrite=True) as temp:
        temp.write_bytes(b"partial")
        raise OSError(errno.ENOSPC, "No space left on device")

    assert error.value.errno == errno.ENOSPC
    assert target.read_bytes() == b"published"
    assert not list(tmp_path.glob("*.part"))


def test_versioned_path(tmp_path: Path) -> None:
    first = tmp_path / "Book.pdf"
    first.write_bytes(b"x")
    assert versioned_path(first).name == "Book_v2.pdf"


def test_atomic_output_versions_existing_file(tmp_path: Path) -> None:
    first = tmp_path / "Book.pdf"
    first.write_bytes(b"old")
    with atomic_output(first, overwrite=False) as temp:
        temp.write_bytes(b"new")
    assert first.read_bytes() == b"old"
    assert (tmp_path / "Book_v2.pdf").read_bytes() == b"new"
