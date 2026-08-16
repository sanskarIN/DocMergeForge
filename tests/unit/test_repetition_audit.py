import zipfile
from pathlib import Path

from docmergeforge.audit.repetition import detect_repeated_front_matter


def _docx(path: Path, part: int) -> None:
    text = (
        "SQL Full Mastery Part "
        f"{part} — Ram Sandesh — August 2026 — Copyright and author information "
        "GitHub github.com/sanskarIN — Buy Me a Coffee buymeacoffee.com/sanskarIN"
    )
    document = f"""<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>
</w:document>
"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)


def test_repeated_front_matter_is_flagged_without_removal(tmp_path: Path) -> None:
    first = tmp_path / "Part 1.docx"
    second = tmp_path / "Part 2.docx"
    _docx(first, 1)
    _docx(second, 2)

    candidates = detect_repeated_front_matter([first, second])
    assert len(candidates) == 1
    assert candidates[0].paths == (first, second)
    assert first.exists() and second.exists()
