from __future__ import annotations

from pathlib import Path

from scripts import check_repository_reference as checker


def test_missing_references_requires_exact_backticked_path() -> None:
    reference = "Files: `alpha.py` and beta.md"

    assert checker.missing_references(reference, ["alpha.py", "beta.md"]) == ["beta.md"]


def test_missing_references_returns_sorted_missing_paths() -> None:
    reference = "`present.txt`"

    assert checker.missing_references(
        reference,
        ["zeta.py", "present.txt", "alpha.md"],
    ) == ["alpha.md", "zeta.py"]


def test_main_passes_when_every_tracked_file_is_referenced(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    reference = tmp_path / "docs" / "repository-reference.md"
    reference.parent.mkdir()
    reference.write_text("`alpha.py`\n`docs/repository-reference.md`\n", encoding="utf-8")
    monkeypatch.setattr(
        checker,
        "tracked_files",
        lambda _root: ["alpha.py", "docs/repository-reference.md"],
    )

    result = checker.main(["--root", str(tmp_path)])

    assert result == 0
    assert "covers all 2 tracked files" in capsys.readouterr().out


def test_main_reports_missing_tracked_files(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    reference = tmp_path / "docs" / "repository-reference.md"
    reference.parent.mkdir()
    reference.write_text("`alpha.py`\n", encoding="utf-8")
    monkeypatch.setattr(checker, "tracked_files", lambda _root: ["alpha.py", "beta.md"])

    result = checker.main(["--root", str(tmp_path)])

    assert result == 1
    output = capsys.readouterr().out
    assert "Tracked files missing" in output
    assert "- beta.md" in output


def test_main_reports_missing_reference_file(tmp_path: Path, capsys) -> None:
    result = checker.main(["--root", str(tmp_path)])

    assert result == 2
    assert "Unable to read repository reference" in capsys.readouterr().out
