import errno
from pathlib import Path

import pytest

import docmergeforge.utilities.storage as storage
from docmergeforge.core.exceptions import OutputAccessError
from docmergeforge.utilities.storage import estimate_storage, require_storage


def test_storage_estimator_accepts_nested_nonexistent_output(tmp_path: Path) -> None:
    source = tmp_path / "part.pdf"
    source.write_bytes(b"x" * 100)
    estimate = estimate_storage([source], tmp_path / "not" / "yet" / "created")
    assert estimate.source_bytes == 100
    assert estimate.free_bytes > 0


def test_require_storage_probes_output_and_cleans_probe(tmp_path: Path) -> None:
    source = tmp_path / "part.pdf"
    source.write_bytes(b"source")
    output = tmp_path / "new" / "output"

    estimate = require_storage([source], output)

    assert estimate.sufficient
    assert output.is_dir()
    assert not list(output.glob(".docmergeforge-write-probe-*"))


def test_require_storage_reports_unwritable_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "output"

    def deny_probe(*_args: object, **_kwargs: object) -> tuple[int, str]:
        raise PermissionError(errno.EACCES, "Permission denied")

    monkeypatch.setattr(storage.tempfile, "mkstemp", deny_probe)

    with pytest.raises(OutputAccessError, match="Output folder is not writable"):
        require_storage([], output)


def test_require_storage_reports_probe_fsync_failure_and_cleans_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "output"

    def failing_fsync(fd: int) -> None:
        del fd
        raise OSError(errno.EIO, "simulated storage flush failure")

    monkeypatch.setattr(storage.os, "fsync", failing_fsync)

    with pytest.raises(OutputAccessError, match="simulated storage flush failure"):
        require_storage([], output)

    assert output.is_dir()
    assert not list(output.glob(".docmergeforge-write-probe-*"))
