from __future__ import annotations

from collections import defaultdict

from docmergeforge.core.models import (
    Diagnostic,
    DiagnosticLevel,
    DocumentKind,
    InputDocument,
    ValidationResult,
)


def validate_part_set(
    documents: list[InputDocument],
    kind: DocumentKind,
    expected_start: int,
    expected_end: int,
    *,
    allow_encrypted_pdf: bool = False,
) -> ValidationResult:
    selected = [item for item in documents if item.kind == kind]
    expected = list(range(expected_start, expected_end + 1))
    by_part: dict[int, list[InputDocument]] = defaultdict(list)
    diagnostics: list[Diagnostic] = []

    for item in selected:
        if item.size == 0:
            diagnostics.append(
                Diagnostic(
                    DiagnosticLevel.ERROR,
                    "Zero-byte input file.",
                    item.path,
                    "Replace the empty input with the correct document.",
                )
            )
        if item.part.number is None:
            diagnostics.append(
                Diagnostic(
                    DiagnosticLevel.WARNING,
                    "Could not detect a part number from the filename.",
                    item.path,
                    "Rename the file or assign a part number manually.",
                )
            )
            continue
        by_part[item.part.number].append(item)
        if kind == DocumentKind.PDF and item.encrypted:
            if allow_encrypted_pdf:
                diagnostics.append(
                    Diagnostic(
                        DiagnosticLevel.INFO,
                        f"Part {item.part.number} PDF password will be supplied in memory.",
                        item.path,
                        "The password is not stored in the project or diagnostics.",
                    )
                )
            else:
                diagnostics.append(
                    Diagnostic(
                        DiagnosticLevel.ERROR,
                        f"Part {item.part.number} PDF is password protected.",
                        item.path,
                        "Provide the password locally before merging.",
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

    found = sorted(part for part in by_part if part in expected)
    missing = [part for part in expected if part not in by_part]
    duplicates = {
        part: [str(item.path) for item in items]
        for part, items in by_part.items()
        if len(items) > 1 and part in expected
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
