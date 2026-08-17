from pathlib import Path

from scripts.check_docs_links import find_broken_links


def test_find_broken_links_accepts_existing_external_and_anchor_links(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (tmp_path / "README.md").write_text(
        "[Docs](docs/guide.md)\n"
        "[Section](docs/guide.md#usage)\n"
        "[Anchor](#top)\n"
        "[Website](https://example.com/docs)\n",
        encoding="utf-8",
    )
    (docs / "guide.md").write_text("# Usage\n", encoding="utf-8")

    assert find_broken_links(tmp_path) == []


def test_find_broken_links_reports_missing_and_outside_targets(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "[Missing](docs/missing.md)\n[Outside](../private.md)\n",
        encoding="utf-8",
    )

    broken = find_broken_links(tmp_path)

    assert [item.target for item in broken] == ["docs/missing.md", "../private.md"]


def test_find_broken_links_decodes_url_encoded_local_paths(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    target = docs / "Build Guide.md"
    target.write_text("# Build\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("[Build](docs/Build%20Guide.md)\n", encoding="utf-8")

    assert find_broken_links(tmp_path) == []


def test_find_broken_links_skips_generated_directories(tmp_path: Path) -> None:
    generated = tmp_path / "build"
    generated.mkdir()
    (generated / "README.md").write_text("[Missing](nope.md)\n", encoding="utf-8")

    assert find_broken_links(tmp_path) == []
