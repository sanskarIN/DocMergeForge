from pathlib import Path

from docmergeforge.ui.recent import RecentProject, RecentProjectsStore


def test_recent_projects_are_deduplicated_and_limited(tmp_path: Path) -> None:
    store = RecentProjectsStore(tmp_path / "recent.json", limit=2)
    one = RecentProject("One", tmp_path / "one.json", tmp_path / "src1", tmp_path / "out1")
    two = RecentProject("Two", tmp_path / "two.json", tmp_path / "src2", tmp_path / "out2")
    three = RecentProject("Three", tmp_path / "three.json", tmp_path / "src3", tmp_path / "out3")

    store.add(one)
    store.add(two)
    store.add(one)
    assert [item.name for item in store.load()] == ["One", "Two"]

    store.add(three)
    assert [item.name for item in store.load()] == ["Three", "One"]
