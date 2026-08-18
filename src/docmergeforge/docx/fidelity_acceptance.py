from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx.fidelity import require_fidelity_automation
from docmergeforge.docx.libreoffice import libreoffice_roundtrip_copy
from docmergeforge.docx.word import word_roundtrip_copy
from docmergeforge.utilities.hashing import sha256_file
from docmergeforge.validation.ooxml import risky_docx_constructs, validate_docx_package


@dataclass(slots=True, frozen=True)
class DocxStructureSnapshot:
    paragraphs: int
    tables: int
    inline_shapes: int
    sections: int
    headings: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class FidelityAcceptanceEvidence:
    mode: str
    source: Path
    output: Path
    source_sha256: str
    output_sha256: str
    source_structure: DocxStructureSnapshot
    output_structure: DocxStructureSnapshot
    source_risks: tuple[str, ...]
    output_risks: tuple[str, ...]
    structure_matches: bool
    new_risks: tuple[str, ...]

    @property
    def accepted(self) -> bool:
        return self.structure_matches and not self.new_risks

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "source": str(self.source),
            "output": str(self.output),
            "source_sha256": self.source_sha256,
            "output_sha256": self.output_sha256,
            "source_structure": self.source_structure.to_dict(),
            "output_structure": self.output_structure.to_dict(),
            "source_risks": list(self.source_risks),
            "output_risks": list(self.output_risks),
            "structure_matches": self.structure_matches,
            "new_risks": list(self.new_risks),
            "accepted": self.accepted,
        }


def snapshot_docx_structure(path: Path) -> DocxStructureSnapshot:
    from docx import Document

    document = Document(str(path))
    headings = sum(
        1
        for paragraph in document.paragraphs
        if paragraph.style and paragraph.style.name.startswith("Heading")
    )
    return DocxStructureSnapshot(
        paragraphs=len(document.paragraphs),
        tables=len(document.tables),
        inline_shapes=len(document.inline_shapes),
        sections=len(document.sections),
        headings=headings,
    )


def _require_valid_docx(path: Path) -> None:
    diagnostics = validate_docx_package(path)
    blocking = [item for item in diagnostics if item.level.value in {"ERROR", "FATAL"}]
    if blocking:
        raise ValidationError(f"DOCX fidelity acceptance input is invalid: {blocking[0].message}")


def run_fidelity_roundtrip_acceptance(
    source: Path,
    output: Path,
    mode: str,
    *,
    timeout_seconds: int = 300,
) -> FidelityAcceptanceEvidence:
    """Run one explicit external-office round-trip and return reviewable evidence.

    Passing this check means the selected file survived the measured structural checks.
    It does not mark the adapter production-ready globally; representative corpus and
    platform acceptance remain separate release gates.
    """
    if mode not in {"libreoffice", "word"}:
        raise ValidationError(
            "Fidelity round-trip acceptance requires mode 'libreoffice' or 'word'."
        )
    capability = require_fidelity_automation(mode)
    _require_valid_docx(source)

    source_sha256 = sha256_file(source)
    source_structure = snapshot_docx_structure(source)
    source_risks = tuple(risky_docx_constructs(source))

    if mode == "libreoffice":
        libreoffice_roundtrip_copy(
            source,
            output,
            executable=capability.executable,
            timeout_seconds=timeout_seconds,
        )
    else:
        word_roundtrip_copy(
            source,
            output,
            powershell=capability.executable,
            timeout_seconds=timeout_seconds,
        )

    _require_valid_docx(output)
    output_structure = snapshot_docx_structure(output)
    output_risks = tuple(risky_docx_constructs(output))
    new_risks = tuple(sorted(set(output_risks) - set(source_risks)))

    return FidelityAcceptanceEvidence(
        mode=mode,
        source=source,
        output=output,
        source_sha256=source_sha256,
        output_sha256=sha256_file(output),
        source_structure=source_structure,
        output_structure=output_structure,
        source_risks=source_risks,
        output_risks=output_risks,
        structure_matches=source_structure == output_structure,
        new_risks=new_risks,
    )
