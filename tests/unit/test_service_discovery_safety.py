from pathlib import Path

from docmergeforge.app.service import MergeApplicationService
from docmergeforge.core.models import MergeProject, MergeSettings


def test_discovery_excludes_strictly_nested_output_subtree(tmp_path: Path) -> None:
    source = tmp_path / "Book"
    output = source / "Master"
    source.mkdir()
    output.mkdir()
    manuscript = source / "Part 1.docx"
    stale_generated_looking_part = output / "Part 2.docx"
    manuscript.write_bytes(b"source")
    stale_generated_looking_part.write_bytes(b"old-output")

    project = MergeProject(
        "Book",
        [source],
        output,
        settings=MergeSettings(expected_start=1, expected_end=2),
    )

    discovered = MergeApplicationService().discover(project)

    assert [item.path for item in discovered] == [manuscript]
