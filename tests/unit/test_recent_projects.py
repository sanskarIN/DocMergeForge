import json
from pathlib import Path

from docmergeforge.ui.recent import RecentProject, RecentProjectsStore


def test_recent_projects_are_deduplicated_and_limited(tmp_path: Path) -> None:
    path = tmp_path / "recent.json"
    store = RecentProjectsStore(path, limit=2)
    one = RecentProject("One", tmp_path / "one.json", tmp_path / "src1", tmp_path / "out1")
    two = RecentProject("Two", tmp_path / "two.json", tmp_path / "src2", tmp_path / "out2")
    three = RecentProject("Three", tmp_path / "three.json", tmp_path / "src3", tmp_path / "out3")

    store.add(one)
    store.add(two)
    store.add(one)
    assert [item.name for item in store.load()] == ["One", "Two"]

    store.add(three)
    assert [item.name for item in store.load()] == ["Three", "One"]
    assert not list(tmp_path.glob(f".{path.name}.*.tmp"))


def test_recent_projects_load_recovers_from_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "recent.json"
    path.write_text("not-json", encoding="utf-8")

    assert RecentProjectsStore(path).load() == []


def test_recent_projects_load_skips_invalid_entries_and_applies_limit(tmp_path: Path) -> None:
    path = tmp_path / "recent.json"
    path.write_text(
        json.dumps(
            [
                {
                    "name": "One",
                    "project_file": str(tmp_path / "one.json"),
                    "source_folder": str(tmp_path / "src1"),
                    "output_folder": str(tmp_path / "out1"),
                },
                {"name": "Incomplete"},
                "invalid",
                {
                    "name": "Two",
                    "project_file": str(tmp_path / "two.json"),
                    "source_folder": str(tmp_path / "src2"),
                    "output_folder": str(tmp_path / "out2"),
                },
            ]
        ),
        encoding="utf-8",
    )

    loaded = RecentProjectsStore(path, limit=1).load()

    assert [item.name for item in loaded] == ["One"]
