from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

from docmergeforge.core.exceptions import MergeCancelled, ValidationError
from docmergeforge.core.models import DocxSettings, InputDocument
from docmergeforge.docx.analysis import PackageCollision, detect_docx_collisions
from docmergeforge.docx.publication import (
    apply_book_headers_footers,
    insert_part_heading,
    insert_toc_field,
    make_page_numbering_continuous,
    normalize_sections_to_first,
)
from docmergeforge.utilities.atomic import atomic_output, versioned_path
from docmergeforge.utilities.hashing import snapshot_hashes, verify_unchanged
from docmergeforge.validation.ooxml import validate_docx_package

Progress = Callable[[int, int, Path], None]
Cancelled = Callable[[], bool]


class DocxMergeEngine:
    @staticmethod
    def analyze_conflicts(documents: list[InputDocument]) -> list[PackageCollision]:
        return detect_docx_collisions([item.path for item in documents])

    def merge(
        self,
        documents: list[InputDocument],
        output: Path,
        settings: DocxSettings,
        *,
        overwrite: bool = False,
        progress: Progress | None = None,
        cancelled: Cancelled | None = None,
    ) -> Path:
        from docx import Document
        from docxcompose.composer import Composer  # type: ignore[import-untyped]

        ordered = sorted(
            documents,
            key=lambda item: (
                item.part.number is None,
                item.part.number or 0,
                item.path.name.casefold(),
            ),
        )
        if not ordered:
            raise ValidationError("No DOCX inputs were provided.")

        before = snapshot_hashes(item.path for item in ordered)
        final_output = output if overwrite else versioned_path(output)
        for item in ordered:
            diagnostics = validate_docx_package(item.path)
            if any(diag.level.value in {"ERROR", "FATAL"} for diag in diagnostics):
                raise ValidationError(f"Invalid DOCX input: {item.path}: {diagnostics[0].message}")

        collisions = self.analyze_conflicts(ordered)
        style_collisions = [item for item in collisions if item.category == "style"]
        numbering_collisions = [item for item in collisions if item.category == "numbering"]
        if settings.style_conflict_policy not in {"prefer_master", "error"}:
            raise ValidationError(
                "Portable DOCX mode currently supports style_conflict_policy="
                "'prefer_master' or 'error'. Use a high-fidelity adapter for other policies."
            )
        if settings.numbering_conflict_policy not in {"remap", "error"}:
            raise ValidationError(
                "Portable DOCX mode currently supports numbering_conflict_policy='remap' or 'error'."
            )
        if settings.style_conflict_policy == "error" and style_collisions:
            raise ValidationError(
                f"DOCX style conflicts require review: {len(style_collisions)} conflict(s)."
            )
        if settings.numbering_conflict_policy == "error" and numbering_collisions:
            raise ValidationError(
                f"DOCX numbering conflicts require review: {len(numbering_collisions)} conflict(s)."
            )

        with atomic_output(final_output, overwrite=True) as temporary:
            master = Document(str(ordered[0].path))
            if settings.add_part_headings:
                first = ordered[0]
                title = first.part.title or first.path.stem
                insert_part_heading(master, f"{first.part.label} — {title}")
            if settings.create_toc_field:
                insert_toc_field(master)

            composer = Composer(master)
            for index, item in enumerate(ordered[1:], start=2):
                if cancelled and cancelled():
                    raise MergeCancelled("DOCX merge cancelled safely.")
                source = Document(str(item.path))
                if settings.start_each_part_on_new_page:
                    master.add_page_break()  # type: ignore[no-untyped-call]
                if settings.add_part_headings:
                    title = item.part.title or item.path.stem
                    master.add_heading(f"{item.part.label} — {title}", level=1)
                composer.append(source)
                if progress:
                    progress(index, len(ordered), item.path)

            if not settings.preserve_sections:
                normalize_sections_to_first(master)
            if settings.continuous_page_numbering:
                make_page_numbering_continuous(master)
            apply_book_headers_footers(master, settings.header_text, settings.footer_text)
            composer.save(str(temporary))

            diagnostics = validate_docx_package(temporary)
            if any(diag.level.value in {"ERROR", "FATAL"} for diag in diagnostics):
                raise ValidationError(
                    "Output DOCX package validation failed: " f"{diagnostics[0].message}"
                )

            Document(str(temporary))
            changed = verify_unchanged(before)
            if changed:
                raise ValidationError(f"Source integrity violation: {changed}")

        return final_output

    @staticmethod
    def high_fidelity_available() -> bool:
        return shutil.which("libreoffice") is not None or shutil.which("soffice") is not None
