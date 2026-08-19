from __future__ import annotations

MAX_PART_NUMBER = 999_999
MAX_EXPECTED_PART_COUNT = 10_000


def validate_expected_part_range(start: int, end: int) -> tuple[int, int]:
    """Validate a bounded expected-part range shared by CLI, projects, and services."""
    if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int):
        raise ValueError("Expected part range values must be integers.")
    if start < 1 or end < start:
        raise ValueError("Expected part range must be positive and non-decreasing.")
    if end > MAX_PART_NUMBER:
        raise ValueError(f"Expected part numbers cannot exceed {MAX_PART_NUMBER}.")
    count = end - start + 1
    if count > MAX_EXPECTED_PART_COUNT:
        raise ValueError(
            f"Expected part range cannot contain more than {MAX_EXPECTED_PART_COUNT} parts."
        )
    return start, end
