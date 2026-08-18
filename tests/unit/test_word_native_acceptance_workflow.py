from pathlib import Path


def _workflow_text() -> str:
    repository_root = Path(__file__).resolve().parents[2]
    workflow = repository_root / ".github" / "workflows" / "word-native-acceptance.yml"
    return workflow.read_text(encoding="utf-8")


def test_word_native_acceptance_requires_controlled_self_hosted_runner() -> None:
    workflow = _workflow_text()

    assert "runs-on: [self-hosted, Windows, X64, docmergeforge-word]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "ubuntu-latest" not in workflow
    assert "windows-latest" not in workflow


def test_word_native_acceptance_keeps_production_policy_disabled() -> None:
    workflow = _workflow_text()

    assert "fidelity-capabilities.json" in workflow
    assert "if ($word.production_ready)" in workflow
    assert "must remain production_ready=false" in workflow


def test_word_native_acceptance_checks_process_state_before_and_after() -> None:
    workflow = _workflow_text()

    assert "check_word_process_state.ps1" in workflow
    assert "-Phase before" in workflow
    assert "-Phase after" in workflow
    assert "word-process-before.json" in workflow
    assert "word-process-after.json" in workflow
    assert "Microsoft Word process cleanup acceptance failed" in workflow


def test_word_native_acceptance_runs_controlled_timeout_cleanup() -> None:
    workflow = _workflow_text()

    assert "timeout_cleanup_seconds:" in workflow
    assert "check_word_timeout_cleanup_acceptance.py" in workflow
    assert "id: word_timeout_cleanup" in workflow
    assert "word-timeout-cleanup-evidence.json" in workflow
    assert "Microsoft Word timeout cleanup acceptance did not pass" in workflow
    assert "steps.word_timeout_cleanup.outcome" in workflow


def test_word_native_acceptance_preserves_evidence_on_failure() -> None:
    workflow = _workflow_text()

    assert "Upload Word acceptance evidence" in workflow
    assert "if: always()" in workflow
    assert "if-no-files-found: error" in workflow
    assert "word-native-merge-evidence.json" in workflow
    assert "word-timeout-cleanup-evidence.json" in workflow
