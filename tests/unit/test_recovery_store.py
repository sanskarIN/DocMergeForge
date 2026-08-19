from pathlib import Path

import pytest

import docmergeforge.project.recovery as recovery_module
from docmergeforge.core.models import MergeProject
from docmergeforge.project.recovery import RecoveryStore


def _project(tmp_path: Path) -> MergeProject:
    return MergeProject(
        name="Book",
        source_folders=[tmp_path / "source"],
        output_folder=tmp_path / "output",
    )


def test_checkpoint_updates_project_only_after_persisted_save(tmp_path: Path) -> None:
    project = _project(tmp_path)
    store = RecoveryStore(tmp_path / "recovery")

    path = store.checkpoint(project, "validated")

    assert path.is_file()
    assert project.last_successful_checkpoint == "validated"
    recovered = store.recover()
    assert recovered is not None
    assert recovered.last_successful_checkpoint == "validated"


def test_checkpoint_does_not_claim_failed_persistence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = _project(tmp_path)
    project.last_successful_checkpoint = "discovered"
    store = RecoveryStore(tmp_path / "recovery")

    def failing_save(project_to_save: MergeProject, path: Path) -> None:
        del project_to_save, path
        raise OSError("simulated checkpoint save failure")

    monkeypatch.setattr(recovery_module, "save_project", failing_save)

    with pytest.raises(OSError, match="simulated checkpoint save failure"):
        store.checkpoint(project, "validated")

    assert project.last_successful_checkpoint == "discovered"
