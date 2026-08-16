import zipfile
from pathlib import Path

from docmergeforge.audit.document import audit_document


def test_docx_audit_finds_stale_next_part_reference(tmp_path: Path) -> None:
    path = tmp_path / "Part 120.docx"
    document = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>Next: Part 121</w:t></w:r></w:p></w:body>
</w:document>
"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)

    findings = audit_document(path)
    assert any(item.code == "stale-next-part" for item in findings)
