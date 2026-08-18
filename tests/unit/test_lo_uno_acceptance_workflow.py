from pathlib import Path


def _workflow_text() -> str:
    repository_root = Path(__file__).resolve().parents[2]
    workflow = (
        repository_root
        / ".github"
        / "workflows"
        / "libreoffice-uno-acceptance.yml"
    )
    return workflow.read_text(encoding="utf-8")


def test_supervised_uno_workflow_uses_real_writer_and_system_uno() -> None:
    workflow = _workflow_text()

    assert "runs-on: ubuntu-latest" in workflow
    assert "libreoffice-writer python3-uno" in workflow
    assert '/usr/bin/python3 -c "import uno;' in workflow
    assert "check_libreoffice_uno_merge_smoke.py" in workflow


def test_supervised_uno_workflow_runs_only_supervised_regressions() -> None:
    workflow = _workflow_text()

    assert "test_lo_uno_supervised_merge.py" in workflow
    assert "test_lo_uno_supervised_acceptance.py" in workflow
    assert "test_lo_uno_supervised_smoke.py" in workflow
    assert "libreoffice_merge.py" not in workflow
    assert "check_libreoffice_native_merge_smoke.py" not in workflow


def test_supervised_uno_workflow_preserves_measured_evidence() -> None:
    workflow = _workflow_text()

    assert "libreoffice-uno-merge-evidence.json" in workflow
    assert "Upload supervised UNO acceptance evidence" in workflow
    assert "if: always()" in workflow
    assert "if-no-files-found: error" in workflow
    assert "supervised-libreoffice-uno-acceptance-evidence" in workflow
