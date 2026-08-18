import json
from pathlib import Path

import pytest
from docx import Document

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx import word_merge
from docmergeforge.docx.native import NativeCommandResult


def _write_docx(path: Path) -> None:
    document = Document()
    document.add_paragraph("Body")
    document.save(path)


def test_word_native_merge_surfaces_cleanup_failure_over_original_timeout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source.docx"
    output = tmp_path / "merged.docx"
    _write_docx(source)

    def failing_run(
        command: list[str], *, timeout_seconds: int
    ) -> NativeCommandResult:
        identity = Path(command[command.index("-ProcessIdentityFile") + 1])
        identity.write_text(
            json.dumps(
                {
                    "process_id": 4242,
                    "process_name": "WINWORD",
                    "start_time_utc_ticks": 638910000000000000,
                }
            ),
            encoding="utf-8",
        )
        raise ValidationError(
            f"Native DOCX fidelity command timed out after {timeout_seconds} seconds."
        )

    def failing_cleanup(identity_file: Path, *, powershell: str) -> object:
        raise ValidationError(
            f"Exact Word cleanup failed for {identity_file.name} via {powershell}."
        )

    monkeypatch.setattr(word_merge, "run_native_command", failing_run)
    monkeypatch.setattr(word_merge, "cleanup_word_process_identity", failing_cleanup)

    with pytest.raises(
        ValidationError,
        match="native merge failed and exact-process cleanup also failed",
    ):
        word_merge.word_merge_documents(
            [source],
            output,
            powershell="fake-powershell",
            timeout_seconds=1,
        )

    assert not output.exists()
