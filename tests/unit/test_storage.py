from pathlib import Path

from docmergeforge.utilities.storage import estimate_storage


def test_storage_estimator_accepts_nested_nonexistent_output(tmp_path: Path) -> None:
    source = tmp_path / "part.pdf"
    source.write_bytes(b"x" * 100)
    estimate = estimate_storage([source], tmp_path / "not" / "yet" / "created")
    assert estimate.source_bytes == 100
    assert estimate.free_bytes > 0
