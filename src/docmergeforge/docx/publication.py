from __future__ import annotations

from typing import Any

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def insert_part_heading(document: Any, text: str) -> None:
    if document.paragraphs:
        paragraph = document.paragraphs[0].insert_paragraph_before(text)
        paragraph.style = "Heading 1"
    else:
        document.add_heading(text, level=1)


def insert_toc_field(document: Any) -> None:
    if document.paragraphs:
        paragraph = document.paragraphs[0].insert_paragraph_before()
    else:
        paragraph = document.add_paragraph()
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(_XML_SPACE, "preserve")
    instruction.text = ' TOC \\o "1-3" \\h \\z \\u '
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Right-click and update field if Word does not refresh automatically."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, placeholder, end])

    settings = document.settings.element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")


def apply_book_headers_footers(document: Any, header: str | None, footer: str | None) -> None:
    for section in document.sections:
        if header is not None:
            section.header.paragraphs[0].text = header
        if footer is not None:
            section.footer.paragraphs[0].text = footer


def make_page_numbering_continuous(document: Any) -> None:
    for section in document.sections:
        section_properties = section._sectPr
        for node in list(section_properties.findall(qn("w:pgNumType"))):
            section_properties.remove(node)


def normalize_sections_to_first(document: Any) -> None:
    if not document.sections:
        return
    first = document.sections[0]
    for section in document.sections[1:]:
        section.page_width = first.page_width
        section.page_height = first.page_height
        section.orientation = first.orientation
        section.top_margin = first.top_margin
        section.bottom_margin = first.bottom_margin
        section.left_margin = first.left_margin
        section.right_margin = first.right_margin
        section.header_distance = first.header_distance
        section.footer_distance = first.footer_distance
