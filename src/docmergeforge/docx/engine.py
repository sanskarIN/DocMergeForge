from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

from docmergeforge.core.exceptions import MergeCancelled, ValidationError
from docmergeforge.core.models import DocxSettings, InputDocument
from docmergeforge.utilities.atomic import atomic_output, versioned_path
from docmergeforge.utilities.hashing import snapshot_hashes, verify_unchanged
from docmergeforge.validation.ooxml import validate_docx_package

Progress = Callable[[int, int, Path], None]
Cancelled = Callable[[], bool]


class DocxMergeEngine:
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

        with atomic_output(final_output, overwrite=True) as temporary:
            master = Document(str(ordered[0].path))
            composer = Composer(master)
            for index, item in enumerate(ordered[1:], start=2):
                if cancelled and cancelled():
                    raise MergeCancelled("DOCX merge cancelled safely.")
                source = Document(str(item.path))
                if settings.start_each_part_on_new_page:
                    master.add_page_break()  # type: ignore[no-untyped-call]
                composer.append(source)
                if progress:
                    progress(index, len(ordered), item.path)
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
