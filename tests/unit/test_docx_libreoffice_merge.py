import subprocess
from pathlib import Path

import pytest
from docx import Document

from docmergeforge.core.exceptions import UnsupportedDocumentError, ValidationError
from docmergeforge.docx import libreoffice_merge


def _write_docx(path: Path, text: str = "Body") -> None:
    document = Document()
    document.add_paragraph(text)
    document.save(path)


def test_libreoffice_uno_worker_uses_official_writer_insertion_interfaces() -> None:
    worker = libreoffice_merge._UNO_WORKER

    assert "com.sun.star.bridge.UnoUrlResolver" in worker
    assert "insertDocumentFromURL" in worker
    assert "com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK" in worker
    assert "com.sun.star.style.BreakType" in worker
    assert '"PAGE_BEFORE"' in worker
    assert '"Office Open XML Text"' in worker
    assert "storeAsURL" in worker
    assert "desktop.terminate()" in worker


def test_find_uno_python_accepts_first_interpreter_that_imports_uno(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / "python-first"
    second = tmp_path / "python-second"
    first.write_text("", encoding="utf-8")
    second.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        libreoffice_merge,
        "_candidate_uno_pythons",
        lambda: (str(first), str(second)),
    )

    calls: list[str] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command[0])
        return subprocess.CompletedProcess(
            command,
            1 if command[0] == str(first) else 0,
            "",
            "",
        )

    monkeypatch.setattr(libreoffice_merge.subprocess, "run", fake_run)

    assert libreoffice_merge.find_uno_python() == str(second)
    assert calls == [str(first), str(second)]


def test_libreoffice_native_merge_rejects_duplicate_sources(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    _write_docx(source)

    with pytest.raises(ValidationError, match="Duplicate LibreOffice merge source"):
        libreoffice_merge.libreoffice_merge_documents(
            [source, source],
            tmp_path / "merged.docx",
            executable="fake-soffice",
            uno_python="fake-python",
        )


def test_libreoffice_native_merge_rejects_existing_output(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    output = tmp_path / "merged.docx"
    _write_docx(source)
    _write_docx(output, "Existing")

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        libreoffice_merge.libreoffice_merge_documents(
            [source],
            output,
            executable="fake-soffice",
            uno_python="fake-python",
        )


def test_libreoffice_native_merge_rejects_nonpositive_timeout(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    _write_docx(source)

    with pytest.raises(ValidationError, match="timeout must be at least one second"):
        libreoffice_merge.libreoffice_merge_documents(
            [source],
            tmp_path / "merged.docx",
            executable="fake-soffice",
            uno_python="fake-python",
            timeout_seconds=0,
        )


def test_libreoffice_native_merge_requires_posix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source.docx"
    _write_docx(source)
    monkeypatch.setattr(libreoffice_merge.os, "name", "nt")

    with pytest.raises(UnsupportedDocumentError, match="currently requires POSIX"):
        libreoffice_merge.libreoffice_merge_documents(
            [source],
            tmp_path / "merged.docx",
            executable="fake-soffice",
            uno_python="fake-python",
        )


def test_terminate_process_group_escalates_only_its_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeProcess:
        pid = 4242

        def wait(self, timeout: float) -> int:
            return 0

    existence = iter((True, True, False))
    monkeypatch.setattr(
        libreoffice_merge,
        "_process_group_exists",
        lambda process_group: next(existence),
    )
    monkeypatch.setattr(
        libreoffice_merge,
        "_wait_for_process_group_exit",
        lambda process_group, timeout: False if timeout == 5 else True,
    )
    signals: list[tuple[int, signal.Signals]] = []
    import signal

    monkeypatch.setattr(
        libreoffice_merge.os,
        "killpg",
        lambda group, sig: signals.append((group, sig)),
    )

    libreoffice_merge._terminate_process_group(FakeProcess())  # type: ignore[arg-type]

    assert signals == [(4242, signal.SIGTERM), (4242, signal.SIGKILL)]
