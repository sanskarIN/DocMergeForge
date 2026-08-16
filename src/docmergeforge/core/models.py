from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class DocumentKind(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    COMPANION = "companion"
    OTHER = "other"


class DiagnosticLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class MergeState(StrEnum):
    CREATED = "CREATED"
    DISCOVERING = "DISCOVERING"
    VALIDATING = "VALIDATING"
    READY = "READY"
    MERGING = "MERGING"
    VERIFYING = "VERIFYING"
    REPORTING = "REPORTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(slots=True, frozen=True)
class PartIdentity:
    number: int | None
    label: str
    title: str | None = None


@dataclass(slots=True)
class InputDocument:
    path: Path
    kind: DocumentKind
    part: PartIdentity
    size: int
    sha256: str
    page_count: int | None = None
    encrypted: bool = False
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["path"] = str(self.path)
        result["kind"] = self.kind.value
        return result


@dataclass(slots=True)
class Diagnostic:
    level: DiagnosticLevel
    message: str
    path: Path | None = None
    suggested_action: str | None = None
    technical_details: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level.value,
            "message": self.message,
            "path": str(self.path) if self.path else None,
            "suggested_action": self.suggested_action,
            "technical_details": self.technical_details,
        }


@dataclass(slots=True)
class ValidationResult:
    expected_parts: list[int]
    found_parts: list[int]
    missing_parts: list[int]
    duplicate_parts: dict[int, list[str]]
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return (
            not self.missing_parts
            and not self.duplicate_parts
            and not any(
                item.level in {DiagnosticLevel.ERROR, DiagnosticLevel.FATAL}
                for item in self.diagnostics
            )
        )


@dataclass(slots=True)
class PdfSettings:
    add_part_bookmarks: bool = True
    title: str | None = None
    author: str | None = None
    edition: str | None = None
    include_title_page: bool = False
    visible_toc: bool = False
    page_numbers: bool = False
    page_number_start: int = 1
    header_text: str | None = None
    footer_text: str | None = None
    watermark_text: str | None = None
    optimization: str = "preserve"


@dataclass(slots=True)
class DocxSettings:
    start_each_part_on_new_page: bool = True
    preserve_sections: bool = True
    fidelity_mode: str = "portable"
    add_part_headings: bool = True
    create_toc_field: bool = True
    style_conflict_policy: str = "prefer_master"
    numbering_conflict_policy: str = "remap"
    header_text: str | None = None
    footer_text: str | None = None
    continuous_page_numbering: bool = True


@dataclass(slots=True)
class MergeSettings:
    expected_start: int = 1
    expected_end: int = 120
    checksum_generation: bool = True
    automatic_validation: bool = True
    overwrite: bool = False
    profile_name: str = "Exact Preservation"
    filename_template: str = "{series}_Master"
    pdf: PdfSettings = field(default_factory=PdfSettings)
    docx: DocxSettings = field(default_factory=DocxSettings)


@dataclass(slots=True)
class MergeProject:
    name: str
    source_folders: list[Path]
    output_folder: Path
    settings: MergeSettings = field(default_factory=MergeSettings)
    selected_files: list[Path] = field(default_factory=list)
    state: MergeState = MergeState.CREATED
    last_successful_checkpoint: str | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class OutputArtifact:
    path: Path
    sha256: str
    size: int
    kind: DocumentKind
    validation_passed: bool


@dataclass(slots=True)
class CompanionReference:
    part: int | None
    path: Path
    sha256: str
    size: int


@dataclass(slots=True)
class MergeManifest:
    app_version: str
    timestamp: str
    os_name: str
    profile: str
    source_order: list[dict[str, Any]]
    outputs: list[dict[str, Any]]
    ignored_files: list[str]
    warnings: list[str]
