from pathlib import Path

from docmergeforge.core.models import MergeProject
from docmergeforge.project.store import load_project, save_project


def test_project_round_trip(tmp_path: Path) -> None:
    project = MergeProject("Demo", [tmp_path / "src"], tmp_path / "out")
    path = tmp_path / "docmergeforge-project.json"
    save_project(project, path)
    restored = load_project(path)
    assert restored.name == "Demo"
    assert restored.source_folders == [tmp_path / "src"]
    assert restored.output_folder == tmp_path / "out"
