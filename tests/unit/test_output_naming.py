from pathlib import Path

import pytest

from docmergeforge.core.models import MergeProject, MergeSettings, PdfSettings
from docmergeforge.utilities.output_naming import render_project_basename, safe_basename


def test_safe_basename_removes_cross_platform_invalid_characters() -> None:
    assert safe_basename("Book: Part 1/2? *Draft*") == "Book_Part_1_2_Draft"
    assert safe_basename("CON") == "_CON"
    assert safe_basename("  ") == "DocMergeForge_Master"


def test_safe_basename_bounds_long_unicode_names_with_stable_hash_suffix() -> None:
    original = "पुस्तक" * 80

    first = safe_basename(original)
    second = safe_basename(original)
    different = safe_basename(original + "x")

    assert len(first.encode("utf-8")) <= 180
    assert first == second
    assert first != different
    assert first.rsplit("_", 1)[-1].isalnum()
    assert len(first.rsplit("_", 1)[-1]) == 12


def test_project_filename_template_uses_project_metadata() -> None:
    project = MergeProject(
        name="SQL Full Mastery",
        source_folders=[Path("input")],
        output_folder=Path("output"),
        settings=MergeSettings(
            expected_start=1,
            expected_end=120,
            profile_name="Master eBook",
            filename_template="{series}_{part_count}_{edition}_{profile}",
            pdf=PdfSettings(author="Ram Sandesh", edition="August 2026"),
        ),
    )
    assert render_project_basename(project) == "SQL_Full_Mastery_120_August_2026_Master_eBook"


def test_project_filename_template_rejects_unknown_variables() -> None:
    project = MergeProject(
        name="Book",
        source_folders=[Path("input")],
        output_folder=Path("output"),
        settings=MergeSettings(filename_template="{unknown}"),
    )
    with pytest.raises(ValueError, match="Unsupported filename template"):
        render_project_basename(project)
