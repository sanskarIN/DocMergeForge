from pathlib import Path

import pytest

import docmergeforge.app.service as service_module
from docmergeforge.app.service import MergeApplicationService
from docmergeforge.core.exceptions import MergeCancelled
from docmergeforge.core.models import (
    DocumentKind,
    InputDocument,
    MergeProject,
    MergeSettings,
    PartIdentity,
    ValidationResult,
)
from docmergeforge.utilities.hashing import sha256_file
from docmergeforge.utilities.storage import StorageEstimate


def _input(path: Path, kind: DocumentKind) -> InputDocument:
    path.write_bytes(f"source-{kind.value}".encode())
    return InputDocument(
        path,
        kind,
        PartIdentity(1, "Part 1"),
        path.stat().st_size,
        sha256_file(path),
    )


def _ready_validation() -> ValidationResult:
    return ValidationResult([1], [1], [], {})


def _prepare_service(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[MergeApplicationService, MergeProject, Path, Path]:
    pdf = _input(tmp_path / "Part 1.pdf", DocumentKind.PDF)
    docx = _input(tmp_path / "Part 1.docx", DocumentKind.DOCX)
    output_folder = tmp_path / "output"
    output_folder.mkdir()
    project = MergeProject(
        "Book",
        [tmp_path],
        output_folder,
        MergeSettings(
            expected_end=1,
            overwrite=True,
            checksum_generation=False,
            filename_template="master",
        ),
    )
    service = MergeApplicationService()
    monkeypatch.setattr(service, "discover", lambda _project: [pdf, docx])
    monkeypatch.setattr(
        service_module,
        "validate_part_set",
        lambda *_args, **_kwargs: _ready_validation(),
    )
    monkeypatch.setattr(
        service_module,
        "require_storage",
        lambda *_args, **_kwargs: StorageEstimate(1, 1, 1, 1, 10),
    )
    return service, project, output_folder / "master.pdf", output_folder / "master.docx"


def test_second_format_failure_keeps_previous_published_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, project, pdf_output, docx_output = _prepare_service(tmp_path, monkeypatch)
    pdf_output.write_bytes(b"old-pdf")
    docx_output.write_bytes(b"old-docx")

    def fake_pdf_merge(
        _self: object,
        _documents: object,
        output: Path,
        _settings: object,
        **_kwargs: object,
    ) -> Path:
        output.write_bytes(b"new-pdf")
        return output

    def fail_docx_merge(
        _self: object,
        _documents: object,
        _output: Path,
        _settings: object,
        **_kwargs: object,
    ) -> Path:
        raise MergeCancelled("DOCX merge cancelled safely.")

    monkeypatch.setattr(service_module.PdfMergeEngine, "merge", fake_pdf_merge)
    monkeypatch.setattr(service_module.DocxMergeEngine, "merge", fail_docx_merge)

    with pytest.raises(MergeCancelled, match="DOCX merge cancelled safely"):
        service.run_project(project)

    assert pdf_output.read_bytes() == b"old-pdf"
    assert docx_output.read_bytes() == b"old-docx"
    assert not list(project.output_folder.glob(".docmergeforge-staging-*"))


def test_late_cancellation_before_promotion_keeps_previous_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, project, pdf_output, docx_output = _prepare_service(tmp_path, monkeypatch)
    pdf_output.write_bytes(b"old-pdf")
    docx_output.write_bytes(b"old-docx")
    cancel_requested = False

    def fake_pdf_merge(
        _self: object,
        _documents: object,
        output: Path,
        _settings: object,
        **_kwargs: object,
    ) -> Path:
        output.write_bytes(b"new-pdf")
        return output

    def fake_docx_merge(
        _self: object,
        _documents: object,
        output: Path,
        _settings: object,
        **_kwargs: object,
    ) -> Path:
        nonlocal cancel_requested
        output.write_bytes(b"new-docx")
        cancel_requested = True
        return output

    monkeypatch.setattr(service_module.PdfMergeEngine, "merge", fake_pdf_merge)
    monkeypatch.setattr(service_module.DocxMergeEngine, "merge", fake_docx_merge)

    with pytest.raises(MergeCancelled, match="cancelled safely"):
        service.run_project(project, cancelled=lambda: cancel_requested)

    assert pdf_output.read_bytes() == b"old-pdf"
    assert docx_output.read_bytes() == b"old-docx"
    assert not list(project.output_folder.glob(".docmergeforge-staging-*"))
