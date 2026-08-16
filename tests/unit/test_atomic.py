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
    with pytest.raises(RuntimeError):
        with atomic_output(target):
            raise RuntimeError("boom")
    assert not target.exists()


def test_versioned_path(tmp_path: Path) -> None:
    first = tmp_path / "Book.pdf"
    first.write_bytes(b"x")
    assert versioned_path(first).name == "Book_v2.pdf"
