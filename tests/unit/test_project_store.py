from pathlib import Path

from docmergeforge.core.models import MergeProject
from docmergeforge.project.store import load_project, save_project


def test_project_round_trip(tmp_path: Path) -> None:
    project = MergeProject("Demo", [tmp_path / "src"], tmp_path / "out")
    project.selected_files = [tmp_path / "src" / "Part 2.pdf", tmp_path / "src" / "Part 1.pdf"]
    project.settings.profile_name = "Custom"
    project.settings.filename_template = "{series}_{part_count}_{profile}"
    path = tmp_path / "docmergeforge-project.json"

    save_project(project, path)
    restored = load_project(path)

    assert restored.name == "Demo"
    assert restored.source_folders == [tmp_path / "src"]
    assert restored.output_folder == tmp_path / "out"
    assert restored.selected_files == project.selected_files
    assert restored.settings.profile_name == "Custom"
    assert restored.settings.filename_template == "{series}_{part_count}_{profile}"
    assert not list(tmp_path.glob(f".{path.name}.*.tmp"))
