from pathlib import Path

from docmergeforge.discovery.scanner import scan


def test_scan_deduplicates_same_file_from_overlapping_roots(tmp_path: Path) -> None:
    source = tmp_path / "source"
    nested = source / "nested"
    nested.mkdir(parents=True)
    manuscript = nested / "Part 1.docx"
    manuscript.write_bytes(b"docx-placeholder")

    discovered = scan([source, nested])

    assert [item.path for item in discovered] == [manuscript]
