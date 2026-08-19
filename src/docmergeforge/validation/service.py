from __future__ import annotations

from collections import defaultdict

from docmergeforge.core.models import (
    Diagnostic,
    DiagnosticLevel,
    DocumentKind,
    InputDocument,
    ValidationResult,
)
from docmergeforge.core.part_range import validate_expected_part_range


def validate_part_set(
    documents: list[InputDocument],
    kind: DocumentKind,
    expected_start: int,
    expected_end: int,
    *,
    allow_encrypted_pdf: bool = False,
    merge_documents: list[InputDocument] | None = None,
) -> ValidationResult:
    expected_start, expected_end = validate_expected_part_range(expected_start, expected_end)
    selected = [item for item in documents if item.kind == kind]
    merge_selected = (
        selected
        if merge_documents is None
        else [item for item in merge_documents if item.kind == kind]
    )
    merge_ids = {id(item) for item in merge_selected}
    expected = list(range(expected_start, expected_end + 1))
    expected_set = set(expected)
    by_part: dict[int, list[InputDocument]] = defaultdict(list)
    diagnostics: list[Diagnostic] = []

    for item in selected:
        is_merge_input = id(item) in merge_ids
        if item.size == 0 and is_merge_input:
            diagnostics.append(
                Diagnostic(
                    DiagnosticLevel.ERROR,
                    "Zero-byte input file.",
                    item.path,
                    "Replace the empty input with the correct document.",
                )
            )
        if kind == DocumentKind.PDF and item.encrypted and is_merge_input:
            part_label = (
                f"Part {item.part.number}" if item.part.number is not None else "Selected"
            )
            if allow_encrypted_pdf:
                diagnostics.append(
                    Diagnostic(
                        DiagnosticLevel.INFO,
                        f"{part_label} PDF password will be supplied in memory.",
                        item.path,
                        "The password is not stored in the project or diagnostics.",
                    )
                )
            else:
                diagnostics.append(
                    Diagnostic(
                        DiagnosticLevel.ERROR,
                        f"{part_label} PDF is password protected.",
                        item.path,
                        "Provide the password locally before merging.",
                    )
                )
        if item.part.number is None:
            diagnostics.append(
                Diagnostic(
                    DiagnosticLevel.WARNING,
                    "Could not detect a part number from the filename.",
                    item.path,
                    (
                        "Review the explicit project selection for this file."
                        if is_merge_input
                        else "Automatic merges exclude this file unless it is explicitly selected."
                    ),
                )
            )
            for warning in item.warnings:
                diagnostics.append(
                    Diagnostic(
                        DiagnosticLevel.WARNING,
                        warning,
                        item.path,
                        "Inspect this file before merging.",
                    )
                )
            continue

        by_part[item.part.number].append(item)
        if item.part.number not in expected_set:
            diagnostics.append(
                Diagnostic(
                    DiagnosticLevel.WARNING,
                    f"Part {item.part.number} is outside the configured expected range.",
                    item.path,
                    "Automatic merges exclude it unless it is explicitly selected in a project.",
                )
            )
        for warning in item.warnings:
            diagnostics.append(
                Diagnostic(
                    DiagnosticLevel.WARNING,
                    warning,
                    item.path,
                    "Inspect this file before merging.",
                )
            )

    found = sorted(part for part in by_part if part in expected_set)
    missing = [part for part in expected if part not in by_part]
    duplicates = {
        part: [str(item.path) for item in items]
        for part, items in by_part.items()
        if len(items) > 1 and part in expected_set
    }

    for part in missing:
        diagnostics.append(
            Diagnostic(
                DiagnosticLevel.ERROR,
                f"Part {part} is missing.",
                suggested_action="Add the missing part or change the expected range.",
            )
        )
    for part, paths in duplicates.items():
        diagnostics.append(
            Diagnostic(
                DiagnosticLevel.ERROR,
                f"Part {part} appears more than once.",
                suggested_action="Choose exactly one input for this part.",
                technical_details="; ".join(paths),
            )
        )

    return ValidationResult(expected, found, missing, duplicates, diagnostics)


def duplicate_hashes(documents: list[InputDocument]) -> dict[str, list[str]]:
    by_hash: dict[str, list[str]] = defaultdict(list)
    for item in documents:
        by_hash[item.sha256].append(str(item.path))
    return {digest: paths for digest, paths in by_hash.items() if len(paths) > 1}
