from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from docmergeforge.core.exceptions import MergeCancelled, ValidationError
from docmergeforge.core.models import InputDocument, PdfSettings
from docmergeforge.pdf.rendering import create_overlay, render_front_matter
from docmergeforge.utilities.atomic import atomic_output, versioned_path
from docmergeforge.utilities.hashing import sha256_file, snapshot_hashes, verify_unchanged

Progress = Callable[[int, int, Path], None]
Cancelled = Callable[[], bool]
PasswordProvider = Callable[[Path], str | None]


class PdfMergeEngine:
    def merge(
        self,
        documents: list[InputDocument],
        output: Path,
        settings: PdfSettings,
        *,
        overwrite: bool = False,
        preserve_order: bool = False,
        progress: Progress | None = None,
        cancelled: Cancelled | None = None,
        password_provider: PasswordProvider | None = None,
    ) -> Path:
        from pypdf import PdfReader, PdfWriter

        ordered = (
            list(documents)
            if preserve_order
            else sorted(
                documents,
                key=lambda item: (
                    item.part.number is None,
                    item.part.number or 0,
                    item.path.name.casefold(),
                ),
            )
        )
        if not ordered:
            raise ValidationError("No PDF inputs were provided.")
        before = snapshot_hashes(item.path for item in ordered)
        final_output = output if overwrite else versioned_path(output)

        with atomic_output(final_output, overwrite=True) as temporary:
            writer = PdfWriter()
            front_matter = render_front_matter(ordered, settings)
            for page in front_matter:
                writer.add_page(page)
            expected_pages = len(front_matter)

            for index, item in enumerate(ordered, start=1):
                if cancelled and cancelled():
                    raise MergeCancelled("PDF merge cancelled safely.")
                reader = PdfReader(str(item.path), strict=False)
                if reader.is_encrypted:
                    if password_provider is None:
                        raise ValidationError(
                            f"Encrypted PDF requires a local password: {item.path}"
                        )
                    password = password_provider(item.path)
                    if password is None:
                        raise ValidationError(
                            f"Encrypted PDF password was not provided: {item.path}"
                        )
                    try:
                        decrypted = reader.decrypt(password)
                    except Exception as exc:
                        raise ValidationError(
                            f"Encrypted PDF password could not be verified: {item.path}"
                        ) from exc
                    if not decrypted:
                        raise ValidationError(
                            f"Encrypted PDF password is incorrect: {item.path}"
                        )
                start_page = len(writer.pages)
                for page in reader.pages:
                    writer.add_page(page)
                expected_pages += len(reader.pages)
                if settings.add_part_bookmarks:
                    title = item.part.title or item.path.stem
                    writer.add_outline_item(f"{item.part.label} — {title}", start_page)
                if progress:
                    progress(index, len(ordered), item.path)

            for index, page in enumerate(writer.pages, start=1):
                overlay = create_overlay(
                    float(page.mediabox.width),
                    float(page.mediabox.height),
                    settings,
                    index,
                )
                if overlay is not None:
                    page.merge_page(overlay)
                if settings.optimization in {"balanced", "archive"}:
                    page.compress_content_streams()

            metadata: dict[str, str] = {}
            if settings.title:
                metadata["/Title"] = settings.title
            if settings.author:
                metadata["/Author"] = settings.author
            if settings.edition:
                metadata["/Subject"] = f"Edition: {settings.edition}"
            metadata["/Creator"] = "DocMergeForge — Made by the Sanskar"
            writer.add_metadata(metadata)
            with temporary.open("wb") as handle:
                writer.write(handle)

            check = PdfReader(str(temporary), strict=False)
            if len(check.pages) != expected_pages:
                raise ValidationError(
                    "PDF page validation failed: "
                    f"expected {expected_pages}, got {len(check.pages)}."
                )

            changed = verify_unchanged(before)
            if changed:
                raise ValidationError(f"Source integrity violation: {changed}")

        return final_output

    @staticmethod
    def validate_output(
        path: Path,
        expected_pages: int | None = None,
    ) -> dict[str, object]:
        from pypdf import PdfReader

        reader = PdfReader(str(path), strict=False)
        if reader.is_encrypted:
            raise ValidationError("Output PDF unexpectedly became encrypted.")
        pages = len(reader.pages)
        if expected_pages is not None and pages != expected_pages:
            raise ValidationError(f"Expected {expected_pages} pages but output has {pages}.")
        return {
            "path": str(path),
            "pages": pages,
            "sha256": sha256_file(path),
            "size": path.stat().st_size,
        }
