import signal
import subprocess
from pathlib import Path

import pytest
from docx import Document

from docmergeforge.core.exceptions import UnsupportedDocumentError, ValidationError
from docmergeforge.docx import libreoffice_uno_merge


def _write_docx(path: Path, text: str = "Body") -> None:
    document = Document()
    document.add_paragraph(text)
    document.save(path)


def test_supervised_uno_worker_uses_writer_document_insertion_contract() -> None:
    worker = libreoffice_uno_merge._UNO_WORKER

    assert "com.sun.star.bridge.UnoUrlResolver" in worker
    assert "insertDocumentFromURL" in worker
    assert "com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK" in worker
    assert "com.sun.star.style.BreakType" in worker
    assert '"PAGE_BEFORE"' in worker
    assert '"Office Open XML Text"' in worker
    assert "storeAsURL" in worker
    assert "desktop.terminate()" in worker


def test_supervised_uno_merge_uses_standard_accept_endpoint() -> None:
    source = libreoffice_uno_merge.libreoffice_uno_merge_documents.__code__
    assert source is not None
    module_text = Path(libreoffice_uno_merge.__file__).read_text(encoding="utf-8")
    assert "StarOffice.ServiceManager" in module_text


def test_find_uno_python_uses_first_working_bridge(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / "python-first"
    second = tmp_path / "python-second"
    first.write_text("", encoding="utf-8")
    second.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        libreoffice_uno_merge,
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

    monkeypatch.setattr(libreoffice_uno_merge.subprocess, "run", fake_run)

    assert libreoffice_uno_merge.find_uno_python() == str(second)
    assert calls == [str(first), str(second)]


def test_process_group_wait_reaps_launcher_while_polling(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeProcess:
        pid = 4242
        poll_calls = 0

        def poll(self) -> int | None:
            self.poll_calls += 1
            return 0

    process = FakeProcess()
    group_states = iter((True, False))

    def fake_killpg(process_group: int, sig: int) -> None:
        assert process_group == 4242
        assert sig == 0
        if not next(group_states):
            raise ProcessLookupError

    monkeypatch.setattr(libreoffice_uno_merge.os, "killpg", fake_killpg)
    monkeypatch.setattr(libreoffice_uno_merge.time, "sleep", lambda seconds: None)

    assert libreoffice_uno_merge._wait_for_process_group_exit(
        4242,
        process,  # type: ignore[arg-type]
        1,
    )
    assert process.poll_calls >= 2


def test_process_group_cleanup_escalates_same_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeProcess:
        pid = 4242

        def poll(self) -> int | None:
            return None

        def wait(self, timeout: float) -> int:
            return 0

    monkeypatch.setattr(
        libreoffice_uno_merge,
        "_process_group_exists",
        lambda process_group, process: True,
    )
    wait_results = iter((False, True))
    monkeypatch.setattr(
        libreoffice_uno_merge,
        "_wait_for_process_group_exit",
        lambda process_group, process, timeout: next(wait_results),
    )
    signals: list[tuple[int, signal.Signals]] = []
    monkeypatch.setattr(
        libreoffice_uno_merge.os,
        "killpg",
        lambda group, sig: signals.append((group, sig)),
    )

    libreoffice_uno_merge._terminate_process_group(FakeProcess())  # type: ignore[arg-type]

    assert signals == [(4242, signal.SIGTERM), (4242, signal.SIGKILL)]


def test_supervised_uno_merge_rejects_duplicate_sources(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    _write_docx(source)

    with pytest.raises(ValidationError, match="Duplicate LibreOffice UNO merge source"):
        libreoffice_uno_merge.libreoffice_uno_merge_documents(
            [source, source],
            tmp_path / "merged.docx",
            executable="fake-soffice",
            uno_python="fake-python",
        )


def test_supervised_uno_merge_refuses_existing_output(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    output = tmp_path / "merged.docx"
    _write_docx(source)
    _write_docx(output, "Existing")

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        libreoffice_uno_merge.libreoffice_uno_merge_documents(
            [source],
            output,
            executable="fake-soffice",
            uno_python="fake-python",
        )


def test_supervised_uno_merge_rejects_nonpositive_timeout(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    _write_docx(source)

    with pytest.raises(ValidationError, match="timeout must be at least one second"):
        libreoffice_uno_merge.libreoffice_uno_merge_documents(
            [source],
            tmp_path / "merged.docx",
            executable="fake-soffice",
            uno_python="fake-python",
            timeout_seconds=0,
        )


def test_supervised_uno_merge_requires_posix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source.docx"
    _write_docx(source)
    monkeypatch.setattr(libreoffice_uno_merge.os, "name", "nt")

    with pytest.raises(UnsupportedDocumentError, match="requires POSIX"):
        libreoffice_uno_merge.libreoffice_uno_merge_documents(
            [source],
            tmp_path / "merged.docx",
            executable="fake-soffice",
            uno_python="fake-python",
        )
