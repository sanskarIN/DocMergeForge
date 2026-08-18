from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from docmergeforge.core.exceptions import DocMergeForgeError, ValidationError
from docmergeforge.docx.fidelity_acceptance import (
    FidelityAcceptanceEvidence,
    run_fidelity_roundtrip_acceptance,
)


@dataclass(slots=True, frozen=True)
class FidelityCorpusItem:
    relative_path: Path
    output_relative_path: Path
    evidence: FidelityAcceptanceEvidence | None = None
    error: str | None = None

    @property
    def accepted(self) -> bool:
        return self.evidence is not None and self.evidence.accepted and self.error is None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "source": self.relative_path.as_posix(),
            "output": self.output_relative_path.as_posix(),
            "accepted": self.accepted,
            "error": self.error,
        }
        if self.evidence is not None:
            evidence_payload = self.evidence.to_dict()
            evidence_payload["source"] = self.relative_path.as_posix()
            evidence_payload["output"] = self.output_relative_path.as_posix()
            payload["evidence"] = evidence_payload
        else:
            payload["evidence"] = None
        return payload


@dataclass(slots=True, frozen=True)
class FidelityCorpusReport:
    mode: str
    pattern: str
    recursive: bool
    items: tuple[FidelityCorpusItem, ...]

    @property
    def accepted_count(self) -> int:
        return sum(1 for item in self.items if item.accepted)

    @property
    def failed_count(self) -> int:
        return len(self.items) - self.accepted_count

    @property
    def accepted(self) -> bool:
        return bool(self.items) and self.failed_count == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "pattern": self.pattern,
            "recursive": self.recursive,
            "input_count": len(self.items),
            "accepted_count": self.accepted_count,
            "failed_count": self.failed_count,
            "accepted": self.accepted,
            "items": [item.to_dict() for item in self.items],
        }


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def discover_fidelity_corpus(
    corpus_dir: Path,
    *,
    pattern: str = "*.docx",
    recursive: bool = True,
) -> list[Path]:
    if not corpus_dir.exists() or not corpus_dir.is_dir():
        raise ValidationError(f"DOCX fidelity corpus directory does not exist: {corpus_dir}")
    if not pattern.strip():
        raise ValidationError("DOCX fidelity corpus pattern cannot be empty.")

    iterator = corpus_dir.rglob("*") if recursive else corpus_dir.glob("*")
    normalized_pattern = pattern.casefold()
    return sorted(
        (
            path
            for path in iterator
            if path.is_file()
            and path.suffix.casefold() == ".docx"
            and fnmatch.fnmatch(path.name.casefold(), normalized_pattern)
        ),
        key=lambda path: path.relative_to(corpus_dir).as_posix().casefold(),
    )


def run_fidelity_corpus(
    corpus_dir: Path,
    output_dir: Path,
    mode: str,
    *,
    pattern: str = "*.docx",
    recursive: bool = True,
    timeout_seconds: int = 300,
    fail_fast: bool = False,
) -> FidelityCorpusReport:
    corpus_root = corpus_dir.resolve()
    output_root = output_dir.resolve()
    if corpus_root == output_root or _is_relative_to(output_root, corpus_root):
        raise ValidationError(
            "Fidelity corpus output directory must be outside the source corpus directory."
        )

    sources = discover_fidelity_corpus(corpus_root, pattern=pattern, recursive=recursive)
    if not sources:
        raise ValidationError(
            f"No DOCX files matched fidelity corpus pattern {pattern!r} in {corpus_root}."
        )

    roundtrip_root = output_root / "roundtrip"
    items: list[FidelityCorpusItem] = []
    for source in sources:
        relative = source.relative_to(corpus_root)
        output_relative = Path("roundtrip") / relative
        destination = output_root / output_relative
        try:
            evidence = run_fidelity_roundtrip_acceptance(
                source,
                destination,
                mode,
                timeout_seconds=timeout_seconds,
            )
        except (DocMergeForgeError, OSError) as exc:
            items.append(
                FidelityCorpusItem(
                    relative_path=relative,
                    output_relative_path=output_relative,
                    error=str(exc),
                )
            )
            if fail_fast:
                break
        else:
            items.append(
                FidelityCorpusItem(
                    relative_path=relative,
                    output_relative_path=output_relative,
                    evidence=evidence,
                )
            )

    roundtrip_root.mkdir(parents=True, exist_ok=True)
    return FidelityCorpusReport(
        mode=mode,
        pattern=pattern,
        recursive=recursive,
        items=tuple(items),
    )


def write_fidelity_corpus_report(report: FidelityCorpusReport, destination: Path) -> Path:
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite fidelity corpus report: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return destination
