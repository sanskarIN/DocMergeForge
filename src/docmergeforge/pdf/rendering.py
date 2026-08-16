from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
from reportlab.pdfgen import canvas  # type: ignore[import-untyped]

from docmergeforge.core.models import InputDocument, PdfSettings

if TYPE_CHECKING:
    from pypdf._page import PageObject


def _pdf_pages(buffer: BytesIO) -> list[PageObject]:
    from pypdf import PdfReader

    buffer.seek(0)
    return list(PdfReader(buffer).pages)


def render_front_matter(
    documents: list[InputDocument],
    settings: PdfSettings,
) -> list[PageObject]:
    pages: list[PageObject] = []
    if settings.include_title_page:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        pdf.setTitle(settings.title or "DocMergeForge Master Edition")
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawCentredString(width / 2, height * 0.66, settings.title or "Master Edition")
        if settings.author:
            pdf.setFont("Helvetica", 14)
            pdf.drawCentredString(width / 2, height * 0.56, f"Author: {settings.author}")
        if settings.edition:
            pdf.drawCentredString(width / 2, height * 0.51, f"Edition: {settings.edition}")
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(width / 2, 56, "Made by the Sanskar")
        pdf.save()
        pages.extend(_pdf_pages(buffer))

    if settings.visible_toc:
        entries_per_page = 34
        page_count = max(1, (len(documents) + entries_per_page - 1) // entries_per_page)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        source_pages = [item.page_count or 0 for item in documents]
        front_count = len(pages) + page_count
        running_page = front_count + 1
        for page_index in range(page_count):
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString(56, height - 64, "Table of Contents")
            pdf.setFont("Helvetica", 10)
            y = height - 100
            start = page_index * entries_per_page
            stop = min(start + entries_per_page, len(documents))
            for index in range(start, stop):
                item = documents[index]
                title = item.part.title or item.path.stem
                label = f"{item.part.label} — {title}"
                if len(label) > 82:
                    label = label[:79] + "..."
                pdf.drawString(56, y, label)
                pdf.drawRightString(width - 56, y, str(running_page))
                y -= 20
                running_page += source_pages[index]
            pdf.setFont("Helvetica", 9)
            pdf.drawCentredString(width / 2, 36, f"Contents {page_index + 1}/{page_count}")
            pdf.showPage()
        pdf.save()
        pages.extend(_pdf_pages(buffer))
    return pages


def create_overlay(
    width: float,
    height: float,
    settings: PdfSettings,
    page_number: int,
) -> PageObject | None:
    if not any(
        (
            settings.page_numbers,
            settings.header_text,
            settings.footer_text,
            settings.watermark_text,
        )
    ):
        return None

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(width, height))
    pdf.setFont("Helvetica", 8)
    if settings.header_text:
        pdf.drawCentredString(width / 2, height - 22, settings.header_text)
    footer = settings.footer_text or ""
    if settings.page_numbers:
        number = settings.page_number_start + page_number - 1
        footer = f"{footer}   •   {number}" if footer else str(number)
    if footer:
        pdf.drawCentredString(width / 2, 18, footer)
    if settings.watermark_text:
        pdf.saveState()
        pdf.setFillGray(0.75, 0.24)
        pdf.setFont("Helvetica-Bold", min(54, max(24, width / 10)))
        pdf.translate(width / 2, height / 2)
        pdf.rotate(38)
        pdf.drawCentredString(0, 0, settings.watermark_text)
        pdf.restoreState()
    pdf.save()
    rendered = _pdf_pages(buffer)
    return rendered[0] if rendered else None
