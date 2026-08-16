import zipfile
from pathlib import Path

from docmergeforge.validation.ooxml import validate_docx_package

_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
</Types>
"""
_DOCUMENT = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body/>
</w:document>
"""
_ROOT_RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def _write_minimal_docx(path: Path, document_rels: str | None = None) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", _CONTENT_TYPES)
        archive.writestr("word/document.xml", _DOCUMENT)
        archive.writestr("_rels/.rels", _ROOT_RELS)
        if document_rels is not None:
            archive.writestr("word/_rels/document.xml.rels", document_rels)


def test_ooxml_relationships_resolve_for_minimal_package(tmp_path: Path) -> None:
    path = tmp_path / "ok.docx"
    _write_minimal_docx(path)
    assert not [item for item in validate_docx_package(path) if item.level.value == "ERROR"]


def test_ooxml_reports_missing_relationship_target(tmp_path: Path) -> None:
    path = tmp_path / "missing-media.docx"
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId7" Type="image" Target="media/missing.png"/>
</Relationships>
"""
    _write_minimal_docx(path, rels)
    messages = [item.message for item in validate_docx_package(path)]
    assert "Unresolved relationship target: word/media/missing.png" in messages


def test_ooxml_reports_duplicate_relationship_ids(tmp_path: Path) -> None:
    path = tmp_path / "duplicate-rid.docx"
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId2" Type="one" Target="../document.xml"/>
  <Relationship Id="rId2" Type="two" Target="../document.xml"/>
</Relationships>
"""
    _write_minimal_docx(path, rels)
    messages = [item.message for item in validate_docx_package(path)]
    assert any("Duplicate relationship Id rId2" in message for message in messages)
