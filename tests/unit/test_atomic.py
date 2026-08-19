import errno
from pathlib import Path

import pytest

from docmergeforge.utilities import atomic
from docmergeforge.utilities.atomic import atomic_output, atomic_write_text, versioned_path


def test_atomic_write_text_replaces_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "settings.json"
    target.write_text("old", encoding="utf-8")

    atomic_write_text(target, "new")

    assert target.read_text(encoding="utf-8") == "new"
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))


def test_atomic_write_text_preserves_target_and_cleans_temp_on_replace_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "settings.json"
    target.write_text("published", encoding="utf-8")

    def failing_replace(source: Path | str, destination: Path | str) -> None:
        del source, destination
        raise OSError(errno.EIO, "simulated replacement failure")

    monkeypatch.setattr(atomic.os, "replace", failing_replace)

    with pytest.raises(OSError, match="simulated replacement failure"):
        atomic_write_text(target, "new")

    assert target.read_text(encoding="utf-8") == "published"
    assert not list(tmp_path.glob(f".{target.name}.*.tmp"))


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


def test_atomic_output_preserves_published_file_when_fsync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "out.bin"
    target.write_bytes(b"published")

    def failing_fsync(fd: int) -> None:
        del fd
        raise OSError(errno.EIO, "simulated fsync failure")

    monkeypatch.setattr(atomic.os, "fsync", failing_fsync)

    with pytest.raises(OSError, match="simulated fsync failure"), atomic_output(
        target, overwrite=True
    ) as temp:
        temp.write_bytes(b"new")

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
