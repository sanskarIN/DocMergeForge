from __future__ import annotations

import os
import shutil
import signal
import subprocess
import tempfile
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.exceptions import UnsupportedDocumentError, ValidationError
from docmergeforge.docx.libreoffice import find_libreoffice
from docmergeforge.docx.native import (
    validate_native_docx_output,
    verify_native_source_unchanged,
)
from docmergeforge.utilities.hashing import sha256_file

_UNO_WORKER = r'''
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import uno


def _property(name: str, value: object) -> object:
    item = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    item.Name = name
    item.Value = value
    return item


def _connect(pipe_name: str, timeout_seconds: int) -> tuple[object, object]:
    local_context = uno.getComponentContext()
    resolver = local_context.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver",
        local_context,
    )
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            remote_context = resolver.resolve(
                f"uno:pipe,name={pipe_name};urp;StarOffice.ComponentContext"
            )
            desktop = remote_context.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop",
                remote_context,
            )
            return remote_context, desktop
        except Exception as exc:
            last_error = exc
            time.sleep(0.2)
    raise RuntimeError(
        f"Could not connect to isolated LibreOffice pipe {pipe_name!r}."
    ) from last_error


def _insert_document(
    document: object,
    source: Path,
    *,
    start_on_new_page: bool,
) -> None:
    text = document.getText()
    cursor = text.createTextCursor()
    cursor.gotoEnd(False)
    paragraph_break = uno.getConstantByName(
        "com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK"
    )
    text.insertControlCharacter(cursor, paragraph_break, False)
    if start_on_new_page:
        cursor.setPropertyValue(
            "BreakType",
            uno.Enum("com.sun.star.style.BreakType", "PAGE_BEFORE"),
        )
    cursor.insertDocumentFromURL(source.resolve().as_uri(), ())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipe-name", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--connect-timeout", type=int, default=30)
    parser.add_argument("--start-each-on-new-page", choices=("0", "1"), default="1")
    args = parser.parse_args()

    sources = [Path(item) for item in json.loads(args.manifest.read_text(encoding="utf-8"))]
    if not sources:
        raise RuntimeError("LibreOffice UNO merge manifest contains no sources.")

    _remote_context, desktop = _connect(args.pipe_name, args.connect_timeout)
    document = None
    try:
        document = desktop.loadComponentFromURL(
            sources[0].resolve().as_uri(),
            "_blank",
            0,
            (_property("Hidden", True),),
        )
        if document is None:
            raise RuntimeError("LibreOffice Writer could not load the master working copy.")
        for source in sources[1:]:
            _insert_document(
                document,
                source,
                start_on_new_page=args.start_each_on_new_page == "1",
            )
        document.storeAsURL(
            args.output.resolve().as_uri(),
            (
                _property("FilterName", "Office Open XML Text"),
                _property("Overwrite", True),
            ),
        )
    finally:
        if document is not None:
            try:
                document.close(True)
            except Exception:
                try:
                    document.dispose()
                except Exception:
                    pass
        try:
            desktop.terminate()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''.strip()


@dataclass(slots=True, frozen=True)
class LibreOfficeNativeMergeResult:
    source_count: int
    output: Path
    worker_stdout: str
    worker_stderr: str


def _validate_sources(sources: Sequence[Path], destination: Path) -> tuple[Path, ...]:
    if not sources:
        raise ValidationError("LibreOffice native merge requires at least one DOCX source.")
    if destination.suffix.casefold() != ".docx":
        raise ValidationError("LibreOffice native merge output must use .docx.")

    normalized = tuple(Path(source) for source in sources)
    destination_resolved = destination.resolve()
    resolved_sources: set[Path] = set()
    for source in normalized:
        if source.suffix.casefold() != ".docx":
            raise ValidationError(f"LibreOffice native merge accepts DOCX files only: {source}")
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(source)
        resolved = source.resolve()
        if resolved == destination_resolved:
            raise ValidationError("LibreOffice native merge requires a separate output path.")
        if resolved in resolved_sources:
            raise ValidationError(f"Duplicate LibreOffice merge source detected: {source}")
        resolved_sources.add(resolved)
        validate_native_docx_output(source)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing DOCX output: {destination}")
    return normalized


def _candidate_uno_pythons() -> tuple[str, ...]:
    candidates: list[str] = []
    configured = os.environ.get("DOCMERGEFORGE_UNO_PYTHON")
    if configured:
        candidates.append(configured)
    candidates.extend(("/usr/bin/python3", "/usr/lib/libreoffice/program/python"))
    discovered = shutil.which("python3")
    if discovered:
        candidates.append(discovered)
    return tuple(dict.fromkeys(candidates))


def find_uno_python() -> str | None:
    """Find a Python interpreter that can import LibreOffice's `uno` module."""
    for candidate in _candidate_uno_pythons():
        path = Path(candidate)
        executable = str(path) if path.is_absolute() else shutil.which(candidate)
        if not executable or not Path(executable).exists():
            continue
        try:
            result = subprocess.run(
                [executable, "-c", "import uno"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode == 0:
            return executable
    return None


def _terminate_process_group(process: subprocess.Popen[str]) -> None:
    """Terminate only the isolated POSIX process group created for LibreOffice."""
    process_group = process.pid
    try:
        os.killpg(process_group, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process_group, signal.SIGKILL)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired as exc:
        raise ValidationError(
            "Isolated LibreOffice process group did not terminate after SIGKILL."
        ) from exc


def libreoffice_merge_documents(
    sources: Sequence[Path],
    destination: Path,
    *,
    executable: str | None = None,
    uno_python: str | None = None,
    timeout_seconds: int = 300,
    start_each_on_new_page: bool = True,
) -> LibreOfficeNativeMergeResult:
    """Merge DOCX files through an isolated LibreOffice Writer UNO session.

    This is a POSIX acceptance prototype, not a production engine. It launches a unique
    LibreOffice user profile and pipe in a new process group so failure cleanup never
    targets a user's normal office session.
    """
    if os.name != "posix":
        raise UnsupportedDocumentError(
            "LibreOffice UNO multi-document acceptance currently requires POSIX pipe/process-group support."
        )
    if timeout_seconds < 1:
        raise ValidationError("LibreOffice native merge timeout must be at least one second.")

    ordered_sources = _validate_sources(sources, destination)
    office = executable or find_libreoffice()
    if office is None:
        raise UnsupportedDocumentError(
            "LibreOffice/soffice was not detected for native merge acceptance."
        )
    python_host = uno_python or find_uno_python()
    if python_host is None:
        raise UnsupportedDocumentError(
            "LibreOffice UNO Python was not detected. Install the LibreOffice/Python UNO bridge."
        )

    source_hashes = {source: sha256_file(source) for source in ordered_sources}
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="docmergeforge-lo-merge-", dir=destination.parent
    ) as temp_name:
        temp_dir = Path(temp_name)
        profile_dir = temp_dir / "profile"
        profile_dir.mkdir()
        first_copy = temp_dir / "master-working-copy.docx"
        shutil.copy2(ordered_sources[0], first_copy)
        temporary_output = temp_dir / destination.name
        manifest = temp_dir / "sources.json"
        worker = temp_dir / "libreoffice_uno_worker.py"
        pipe_name = f"docmergeforge_{uuid.uuid4().hex}"

        import json

        manifest.write_text(
            json.dumps(
                [str(first_copy.resolve())]
                + [str(source.resolve()) for source in ordered_sources[1:]]
            ),
            encoding="utf-8",
        )
        worker.write_text(_UNO_WORKER, encoding="utf-8")

        office_process = subprocess.Popen(
            [
                office,
                f"-env:UserInstallation={profile_dir.resolve().as_uri()}",
                "--headless",
                "--nologo",
                "--nodefault",
                "--nofirststartwizard",
                "--norestore",
                f"--accept=pipe,name={pipe_name};urp;",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        worker_process: subprocess.Popen[str] | None = None
        worker_stdout = ""
        worker_stderr = ""
        try:
            worker_process = subprocess.Popen(
                [
                    python_host,
                    str(worker),
                    "--pipe-name",
                    pipe_name,
                    "--manifest",
                    str(manifest),
                    "--output",
                    str(temporary_output.resolve()),
                    "--connect-timeout",
                    str(min(timeout_seconds, 30)),
                    "--start-each-on-new-page",
                    "1" if start_each_on_new_page else "0",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                worker_stdout, worker_stderr = worker_process.communicate(
                    timeout=timeout_seconds
                )
            except subprocess.TimeoutExpired as exc:
                worker_process.kill()
                worker_stdout, worker_stderr = worker_process.communicate()
                raise ValidationError(
                    f"LibreOffice UNO merge timed out after {timeout_seconds} seconds."
                ) from exc
            if worker_process.returncode != 0:
                detail = worker_stderr.strip() or worker_stdout.strip()
                raise ValidationError(
                    "LibreOffice UNO merge worker failed"
                    + (f": {detail}" if detail else ".")
                )
        finally:
            if worker_process is not None and worker_process.poll() is None:
                worker_process.kill()
                worker_process.wait(timeout=5)
            _terminate_process_group(office_process)

        validate_native_docx_output(temporary_output)
        for source, expected_hash in source_hashes.items():
            verify_native_source_unchanged(source, expected_hash)
        temporary_output.replace(destination)

    validate_native_docx_output(destination)
    for source, expected_hash in source_hashes.items():
        verify_native_source_unchanged(source, expected_hash)
    return LibreOfficeNativeMergeResult(
        source_count=len(ordered_sources),
        output=destination,
        worker_stdout=worker_stdout,
        worker_stderr=worker_stderr,
    )
