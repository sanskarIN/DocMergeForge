import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from docmergeforge.cli import main as cli
from docmergeforge.core.exceptions import TransactionRecoveryError
from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity
from docmergeforge.utilities.output_transaction import RecoveryResult


def document(name: str, part: int | None) -> InputDocument:
    return InputDocument(
        path=Path(name),
        kind=DocumentKind.PDF,
        part=PartIdentity(part, f"Part {part}" if part is not None else "Unnumbered"),
        size=1,
        sha256=name,
    )


def test_cli_parser_supports_pattern_and_sort_controls() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "pdf",
            "--input",
            "input",
            "--output",
            "master.pdf",
            "--parts",
            "1-12",
            "--pattern",
            "Part *.pdf",
            "--no-natural-sort",
        ]
    )
    assert args.parts == (1, 12)
    assert args.pattern == "Part *.pdf"
    assert args.natural_sort is False


def test_cli_parser_supports_output_recovery() -> None:
    args = cli.build_parser().parse_args(["recover-output", "--output-dir", "artifacts"])
    assert args.command == "recover-output"
    assert args.output_dir == Path("artifacts")


def test_cli_pattern_filter_is_case_insensitive() -> None:
    items = [document("Part 1.PDF", 1), document("notes.pdf", 2)]
    assert cli._filter_pattern(items, "part *.pdf") == [items[0]]


def test_cli_natural_order_uses_part_numbers() -> None:
    items = [document("Part 10.pdf", 10), document("Part 2.pdf", 2)]
    ordered = cli._ordered_items(items, natural_sort=True)
    assert [item.part.number for item in ordered] == [2, 10]


def test_cli_filename_order_can_be_selected() -> None:
    items = [document("Part 2.pdf", 2), document("Part 10.pdf", 10)]
    ordered = cli._ordered_items(items, natural_sort=False)
    assert [item.path.name for item in ordered] == ["Part 10.pdf", "Part 2.pdf"]


def test_cli_password_collection_retries_without_persisting(monkeypatch) -> None:
    item = document("Part 1.pdf", 1)
    item.encrypted = True
    responses = iter(["wrong", "correct"])
    monkeypatch.setattr(cli.getpass, "getpass", lambda _prompt: next(responses))
    monkeypatch.setattr(cli, "verify_pdf_password", lambda _path, value: value == "correct")

    passwords = cli._collect_pdf_passwords([item])

    assert passwords == {item.path: "correct"}


def test_direct_merge_reports_actual_path_and_excludes_unrelated_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    part_1 = document("Part 1.pdf", 1)
    old_master = document("Book Master.pdf", None)
    extra = document("Part 2.pdf", 2)
    requested = tmp_path / "Book.pdf"
    actual = tmp_path / "Book_v2.pdf"
    captured_documents: list[InputDocument] = []

    monkeypatch.setattr(cli, "scan", lambda _folders: [old_master, extra, part_1])
    monkeypatch.setattr(
        cli,
        "validate_part_set",
        lambda *args, **kwargs: SimpleNamespace(
            ready=True,
            missing_parts=[],
            duplicate_parts={},
        ),
    )

    class FakePdfMergeEngine:
        def merge(
            self,
            documents: list[InputDocument],
            *args: object,
            **kwargs: object,
        ) -> Path:
            del self, args, kwargs
            captured_documents.extend(documents)
            return actual

    monkeypatch.setattr(cli, "PdfMergeEngine", FakePdfMergeEngine)
    args = argparse.Namespace(
        command="pdf",
        input=tmp_path,
        parts=(1, 1),
        output=requested,
        pattern=None,
        natural_sort=True,
    )

    exit_code = cli._run_direct_merge(args)

    assert exit_code == 0
    assert captured_documents == [part_1]
    assert capsys.readouterr().out.strip() == str(actual)


def test_cli_project_create_reports_save_failure_as_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project_path = tmp_path / "project.json"

    def fail_save(*_args: object, **_kwargs: object) -> None:
        raise OSError("project destination denied")

    monkeypatch.setattr(cli, "save_project", fail_save)

    exit_code = cli.main(
        [
            "project-create",
            "--input",
            str(tmp_path / "source"),
            "--output-dir",
            str(tmp_path / "output"),
            "--project-file",
            str(project_path),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload == {
        "created": False,
        "project": str(project_path),
        "error": "project destination denied",
    }


def test_cli_recover_output_reports_recovered_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    transaction = tmp_path / ".docmergeforge-staging-crash"
    restored = tmp_path / "master.pdf"
    removed = tmp_path / "new-report.json"
    monkeypatch.setattr(
        cli,
        "recover_interrupted_output_transactions",
        lambda _output: [
            RecoveryResult(
                transaction,
                "rolled-back",
                (restored,),
                (removed,),
            )
        ],
    )

    exit_code = cli.main(["recover-output", "--output-dir", str(tmp_path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert '"recovered": true' in output
    assert '"status": "rolled-back"' in output
    assert str(restored) in output
    assert str(removed) in output


def test_cli_recover_output_fails_closed_on_conflict(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_recovery(_output: Path) -> list[RecoveryResult]:
        raise TransactionRecoveryError("published file changed after interruption")

    monkeypatch.setattr(cli, "recover_interrupted_output_transactions", fail_recovery)

    exit_code = cli.main(["recover-output", "--output-dir", str(tmp_path)])
    output = capsys.readouterr().out

    assert exit_code == 2
    assert '"recovered": false' in output
    assert "published file changed after interruption" in output
