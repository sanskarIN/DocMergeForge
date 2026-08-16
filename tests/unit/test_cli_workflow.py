from pathlib import Path

from docmergeforge.cli import main as cli
from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity


def document(name: str, part: int) -> InputDocument:
    return InputDocument(
        path=Path(name),
        kind=DocumentKind.PDF,
        part=PartIdentity(part, f"Part {part}"),
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
