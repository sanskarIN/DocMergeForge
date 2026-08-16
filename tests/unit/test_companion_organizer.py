import zipfile
from pathlib import Path

import pytest

from docmergeforge.companion.organizer import copy_companion_packages
from docmergeforge.core.models import CompanionReference
from docmergeforge.utilities.hashing import sha256_file


def test_copy_companion_package_is_byte_for_byte_and_not_extracted(tmp_path: Path) -> None:
    source = tmp_path / "Part 1 Companion Code.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("example.sql", "SELECT 1;\n")
    digest = sha256_file(source)
    reference = CompanionReference(1, source, digest, source.stat().st_size)

    destination_root = tmp_path / "organized"
    results = copy_companion_packages([reference], destination_root)

    copied = destination_root / "Part_001" / source.name
    assert results[0].destination == copied
    assert sha256_file(source) == digest
    assert sha256_file(copied) == digest
    assert not (destination_root / "Part_001" / "example.sql").exists()


def test_copy_companion_refuses_to_overwrite_different_file(tmp_path: Path) -> None:
    source = tmp_path / "Part 2 Companion Code.zip"
    source.write_bytes(b"source")
    reference = CompanionReference(2, source, sha256_file(source), source.stat().st_size)
    destination = tmp_path / "organized" / "Part_002" / source.name
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"different")

    with pytest.raises(FileExistsError):
        copy_companion_packages([reference], tmp_path / "organized")
