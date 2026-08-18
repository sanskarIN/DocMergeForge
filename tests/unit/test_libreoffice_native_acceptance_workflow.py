from pathlib import Path


def _workflow_text() -> str:
    repository_root = Path(__file__).resolve().parents[2]
    workflow = (
        repository_root
        / ".github"
        / "workflows"
        / "libreoffice-native-acceptance.yml"
    )
    return workflow.read_text(encoding="utf-8")


def test_libreoffice_native_acceptance_installs_real_writer_and_uno_bridge() -> None:
    workflow = _workflow_text()

    assert "runs-on: ubuntu-latest" in workflow
    assert "libreoffice-writer python3-uno" in workflow
    assert '/usr/bin/python3 -c "import uno;' in workflow
    assert "check_libreoffice_native_merge_smoke.py" in workflow


def test_libreoffice_native_acceptance_keeps_capability_separation_visible() -> None:
    workflow = _workflow_text()

    assert "docmergeforge fidelity-capabilities" in workflow
    assert "LibreOffice Native Merge Acceptance" in workflow
    assert "libreoffice-native-merge-acceptance-evidence" in workflow


def test_libreoffice_native_acceptance_preserves_evidence_on_failure() -> None:
    workflow = _workflow_text()

    assert "Display measured LibreOffice native evidence" in workflow
    assert "Upload LibreOffice native acceptance evidence" in workflow
    assert "if: always()" in workflow
    assert "if-no-files-found: error" in workflow
    assert "libreoffice-native-merge-evidence.json" in workflow
