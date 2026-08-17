from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from docmergeforge.core.models import DocumentKind
from docmergeforge.discovery.scanner import scan
from docmergeforge.validation.service import validate_part_set


@pytest.mark.integration
def test_stress_fixture_generator_creates_valid_numbered_inputs(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "generate_stress_fixture.py"),
            str(tmp_path),
            "--parts",
            "2",
            "--pdf-pages",
            "1",
            "--pdf-lines-per-page",
            "2",
            "--docx-paragraphs",
            "2",
            "--paragraph-kib",
            "1",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )

    items = scan([tmp_path])
    pdf_result = validate_part_set(items, DocumentKind.PDF, 1, 2)
    docx_result = validate_part_set(items, DocumentKind.DOCX, 1, 2)

    assert "parts=2" in result.stdout
    assert pdf_result.ready
    assert docx_result.ready
    assert len([item for item in items if item.kind == DocumentKind.COMPANION]) == 2
