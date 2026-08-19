import argparse

import pytest

from docmergeforge.cli.main import _parts
from docmergeforge.core.part_range import MAX_EXPECTED_PART_COUNT, MAX_PART_NUMBER


def test_cli_parts_accepts_normal_range() -> None:
    assert _parts("1-120") == (1, 120)


def test_cli_parts_rejects_excessive_part_count() -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="cannot contain more than"):
        _parts(f"1-{MAX_EXPECTED_PART_COUNT + 1}")


def test_cli_parts_rejects_part_number_above_detector_limit() -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="cannot exceed"):
        _parts(f"{MAX_PART_NUMBER}-{MAX_PART_NUMBER + 1}")


def test_cli_parts_rejects_malformed_range() -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        _parts("1")
