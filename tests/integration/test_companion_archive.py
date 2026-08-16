from pathlib import Path

import pytest

from docmergeforge.app.companion_archive import create_copy_only_companion_archive
from docmergeforge.utilities.hashing import sha256_file


@pytest.mark.integration
def test_copy_only_archive_preserves_companion_bytes(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    package = source / "Part 7 Companion.zip"
    package.write_bytes(b"PK\x03\x04companion-package-bytes")
    before = sha256_file(package)

    destination = tmp_path / "archive"
    result = create_copy_only_companion_archive([source], destination)

    assert len(result.packages) == 1
    copied = result.packages[0]
    assert copied.destination.read_bytes() == package.read_bytes()
    assert sha256_file(package) == before
    assert sha256_file(copied.destination) == before
    assert result.markdown_index.exists()
    assert result.json_index.exists()


def test_copy_only_archive_rejects_empty_sources(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    with pytest.raises(ValueError, match="No companion package"):
        create_copy_only_companion_archive([source], tmp_path / "archive")
