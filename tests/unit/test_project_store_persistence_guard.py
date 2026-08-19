from pathlib import Path

import pytest

from docmergeforge.core.models import MergeProject
from docmergeforge.core.part_range import MAX_EXPECTED_PART_COUNT
from docmergeforge.project.store import save_project


def test_save_project_rejects_invalid_expected_range_before_writing(tmp_path: Path) -> None:
    project = MergeProject("Demo", [tmp_path / "source"], tmp_path / "output")
    project.settings.expected_end = MAX_EXPECTED_PART_COUNT + 1
    destination = tmp_path / "project.json"

    with pytest.raises(ValueError, match="cannot contain more than"):
        save_project(project, destination)

    assert not destination.exists()
