from collections.abc import Iterator
from pathlib import Path

import pytest

from docmergeforge.discovery import scanner


def test_scan_excludes_nested_files_before_hashing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "Book"
    excluded = source / "Master"
    source.mkdir()
    excluded.mkdir()
    included_file = source / "Part 1.docx"
    excluded_file = excluded / "Part 2.docx"
    included_file.write_text("source", encoding="utf-8")
    excluded_file.write_text("old output", encoding="utf-8")
    hashed: list[Path] = []

    def fake_hash(path: Path) -> str:
        if path == excluded_file:
            raise AssertionError("excluded output reached hashing")
        hashed.append(path)
        return "0" * 64

    monkeypatch.setattr(scanner, "sha256_file", fake_hash)

    discovered = scanner.scan([source], exclude_roots=[excluded])

    assert [item.path for item in discovered] == [included_file]
    assert hashed == [included_file]


def test_scan_excludes_nested_pdf_before_pdf_inspection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "Book"
    excluded = source / "Master"
    source.mkdir()
    excluded.mkdir()
    included_file = source / "Part 1.docx"
    excluded_pdf = excluded / "Part 2.pdf"
    included_file.write_text("source", encoding="utf-8")
    excluded_pdf.write_bytes(b"not a real pdf")

    def fail_pdf_info(path: Path) -> tuple[int | None, bool, list[str]]:
        raise AssertionError(f"excluded PDF reached inspection: {path}")

    monkeypatch.setattr(scanner, "_pdf_info", fail_pdf_info)
    monkeypatch.setattr(scanner, "sha256_file", lambda _path: "0" * 64)

    discovered = scanner.scan([source], exclude_roots=[excluded])

    assert [item.path for item in discovered] == [included_file]


def test_recursive_iter_files_prunes_excluded_directory_before_descent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "Book"
    source.mkdir()
    excluded = source / "Master"
    content = source / "Content"
    directory_names = ["Master", "Content"]
    walk_calls: list[tuple[Path, bool]] = []

    def fake_walk(
        root: Path,
        *,
        followlinks: bool,
    ) -> Iterator[tuple[str, list[str], list[str]]]:
        walk_calls.append((root, followlinks))
        yield str(source), directory_names, ["root.txt"]
        assert directory_names == ["Content"]
        yield str(content), [], ["Part 1.docx"]

    monkeypatch.setattr(scanner.os, "walk", fake_walk)

    discovered = list(scanner.iter_files([source], exclude_roots=[excluded]))

    assert discovered == [source / "root.txt", content / "Part 1.docx"]
    assert walk_calls == [(source, False)]


def test_iter_files_skips_root_that_is_inside_excluded_tree(tmp_path: Path) -> None:
    excluded = tmp_path / "Master"
    nested = excluded / "nested"
    nested.mkdir(parents=True)
    (nested / "Part 1.docx").write_text("output", encoding="utf-8")

    discovered = list(scanner.iter_files([nested], exclude_roots=[excluded]))

    assert discovered == []


def test_non_recursive_iter_files_still_honors_excluded_root(tmp_path: Path) -> None:
    source = tmp_path / "Book"
    excluded = source / "Master"
    excluded.mkdir(parents=True)
    included = source / "Part 1.docx"
    excluded_file = excluded / "Part 2.docx"
    included.write_text("one", encoding="utf-8")
    excluded_file.write_text("two", encoding="utf-8")

    discovered = list(scanner.iter_files([source], recursive=False, exclude_roots=[excluded]))

    assert discovered == [included]


def test_scan_without_exclusions_preserves_existing_behavior(tmp_path: Path) -> None:
    source = tmp_path / "Book"
    nested = source / "nested"
    nested.mkdir(parents=True)
    first = source / "Part 1.docx"
    second = nested / "Part 2.docx"
    first.write_text("one", encoding="utf-8")
    second.write_text("two", encoding="utf-8")

    discovered = scanner.scan([source])

    assert {item.path for item in discovered} == {first, second}
