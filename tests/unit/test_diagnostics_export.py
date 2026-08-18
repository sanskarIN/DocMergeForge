import json
from pathlib import Path

from docmergeforge import __version__
from docmergeforge.diagnostics.export import export_diagnostics


def test_export_diagnostics_writes_privacy_safe_json_atomically(tmp_path: Path) -> None:
    path = tmp_path / "diagnostics" / "report.json"

    result = export_diagnostics(path, ["warning"], ["recent error"])

    assert result == path
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["app_version"] == __version__
    assert payload["warnings"] == ["warning"]
    assert payload["recent_errors"] == ["recent error"]
    assert "Document body text and passwords" in payload["privacy_note"]
    assert payload["generated_at"].endswith("+00:00")
    assert payload["platform"]
    assert not list(path.parent.glob(f".{path.name}.*.tmp"))
