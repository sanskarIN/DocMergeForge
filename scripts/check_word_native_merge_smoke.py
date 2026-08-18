from __future__ import annotations

import argparse
import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT

from docmergeforge.docx.word_merge_acceptance import run_word_merge_acceptance


def _write_fixture(path: Path, title: str, *, landscape: bool) -> None:
    document = Document()
    document.core_properties.title = title
    document.add_heading(title, level=1)
    document.add_paragraph(f"Representative body content for {title}.")
    document.add_paragraph("First numbered item", style="List Number")
    document.add_paragraph("Second numbered item", style="List Number")
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Feature"
    table.cell(0, 1).text = "Value"
    table.cell(1, 0).text = "Source"
    table.cell(1, 1).text = title

    section = document.sections[0]
    if landscape:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = section.page_height, section.page_width
    section.header.paragraphs[0].text = f"Header — {title}"
    section.footer.paragraphs[0].text = f"Footer — {title}"
    document.save(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a synthetic Microsoft Word native multi-document merge smoke."
    )
    parser.add_argument("--output-dir", type=Path, default=Path("word-merge-evidence"))
    parser.add_argument("--timeout", type=int, default=900)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.timeout < 1:
        raise SystemExit("--timeout must be at least one second")

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    first = output_dir / "word-merge-source-01.docx"
    second = output_dir / "word-merge-source-02.docx"
    merged = output_dir / "word-native-merged.docx"
    evidence_path = output_dir / "word-native-merge-evidence.json"
    for path in (first, second, merged, evidence_path):
        if path.exists():
            raise SystemExit(f"Refusing to overwrite existing Word smoke artifact: {path}")

    _write_fixture(first, "Word Native Merge Source 1", landscape=False)
    _write_fixture(second, "Word Native Merge Source 2", landscape=True)
    evidence = run_word_merge_acceptance(
        [first, second],
        merged,
        timeout_seconds=args.timeout,
        start_each_on_new_page=True,
    )
    evidence_path.write_text(
        json.dumps(evidence.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(evidence_path)
    return 0 if evidence.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
