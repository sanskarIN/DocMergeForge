import zipfile
from pathlib import Path

import pytest

from docmergeforge.core.models import DocumentKind, DocxSettings, InputDocument, PartIdentity
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.utilities.hashing import sha256_file


@pytest.mark.integration
def test_docx_adds_part_headings_and_toc_field(tmp_path: Path) -> None:
    docx = pytest.importorskip("docx")
    pytest.importorskip("docxcompose")
    inputs: list[InputDocument] = []
    for part in (1, 2):
        path = tmp_path / f"Part {part}.docx"
        document = docx.Document()
        document.add_paragraph(f"Source body {part}")
        document.save(path)
        inputs.append(
            InputDocument(
                path=path,
                kind=DocumentKind.DOCX,
                part=PartIdentity(part, f"Part {part}", f"Title {part}"),
                size=path.stat().st_size,
                sha256=sha256_file(path),
            )
        )

    output = tmp_path / "master.docx"
    DocxMergeEngine().merge(
        inputs,
        output,
        DocxSettings(
            add_part_headings=True,
            create_toc_field=True,
            footer_text="Made by the Sanskar",
        ),
    )

    reopened = docx.Document(str(output))
    text = "\n".join(paragraph.text for paragraph in reopened.paragraphs)
    assert "Part 1 — Title 1" in text
    assert "Part 2 — Title 2" in text
    with zipfile.ZipFile(output) as archive:
        document_xml = archive.read("word/document.xml")
        settings_xml = archive.read("word/settings.xml")
    assert b"TOC" in document_xml
    assert b"updateFields" in settings_xml
