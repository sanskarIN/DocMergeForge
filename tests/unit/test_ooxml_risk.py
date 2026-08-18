import zipfile
from pathlib import Path

from docmergeforge.validation.ooxml import risky_docx_constructs


_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
</Types>
"""
_ROOT_RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="officeDocument" Target="word/document.xml"/>
</Relationships>
"""
_DOCUMENT = """<?xml version="1.0" encoding="UTF-8"?>
<w:document
  xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <w:body>
    <w:ins><w:r><w:t>revision</w:t></w:r></w:ins>
    <w:sdt><w:sdtContent><w:p/></w:sdtContent></w:sdt>
    <w:fldSimple w:instr="DATE"><w:r><w:t>date</w:t></w:r></w:fldSimple>
    <m:oMath><m:r/></m:oMath>
  </w:body>
</w:document>
"""
_DOCUMENT_RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId8" Type="hyperlink" Target="https://example.com" TargetMode="External"/>
</Relationships>
"""


def test_risky_docx_constructs_reports_complex_ooxml(tmp_path: Path) -> None:
    path = tmp_path / "complex.docx"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", _CONTENT_TYPES)
        archive.writestr("_rels/.rels", _ROOT_RELS)
        archive.writestr("word/document.xml", _DOCUMENT)
        archive.writestr("word/_rels/document.xml.rels", _DOCUMENT_RELS)
        archive.writestr("word/comments.xml", "<comments/>")
        archive.writestr("word/embeddings/object1.bin", b"object")
        archive.writestr("word/charts/chart1.xml", "<chart/>")
        archive.writestr("word/diagrams/data1.xml", "<diagram/>")
        archive.writestr("customXml/item1.xml", "<custom/>")

    risks = set(risky_docx_constructs(path))
    assert "Embedded OLE/package objects detected." in risks
    assert "Custom XML parts detected." in risks
    assert "Comments/annotations detected." in risks
    assert "Charts detected." in risks
    assert "SmartArt/diagram parts detected." in risks
    assert "External relationships detected." in risks
    assert "Tracked insertions/revisions detected." in risks
    assert "Content controls detected." in risks
    assert "Word field codes detected." in risks
    assert "Office Math equations detected." in risks
