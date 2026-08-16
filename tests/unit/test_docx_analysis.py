import zipfile
from pathlib import Path

from docmergeforge.docx.analysis import analyze_docx, detect_docx_collisions

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _write_docx(path: Path, style_color: str, media: bytes) -> None:
    document = f"""<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="{_W}">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Title</w:t></w:r></w:p>
    <w:p><w:r><w:t>Body</w:t></w:r></w:p>
    <w:tbl/>
    <w:sectPr/>
  </w:body>
</w:document>
"""
    styles = f"""<?xml version="1.0" encoding="UTF-8"?>
<w:styles xmlns:w="{_W}">
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="Heading 1"/>
    <w:rPr><w:color w:val="{style_color}"/></w:rPr>
  </w:style>
</w:styles>
"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", styles)
        archive.writestr("word/media/image1.png", media)


def test_docx_inventory_counts_content(tmp_path: Path) -> None:
    path = tmp_path / "Part 1.docx"
    _write_docx(path, "000000", b"image-a")
    inventory = analyze_docx(path)
    assert inventory.paragraphs == 2
    assert inventory.headings == 1
    assert inventory.tables == 1
    assert inventory.sections == 1
    assert inventory.media_items == 1
    assert "Heading 1" in inventory.style_names


def test_docx_collision_report_detects_conflicting_style_and_media(tmp_path: Path) -> None:
    first = tmp_path / "Part 1.docx"
    second = tmp_path / "Part 2.docx"
    _write_docx(first, "000000", b"image-a")
    _write_docx(second, "FF0000", b"image-b")

    collisions = detect_docx_collisions([first, second])
    pairs = {(item.category, item.name) for item in collisions}
    assert ("style", "Heading 1") in pairs
    assert ("media", "word/media/image1.png") in pairs
