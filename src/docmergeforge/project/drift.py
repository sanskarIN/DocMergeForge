from __future__ import annotations

from dataclasses import dataclass

from docmergeforge.core.models import MergeProject
from docmergeforge.project.sync import ProjectSyncPlan, plan_project_sync


@dataclass(slots=True, frozen=True)
class ProjectSyncDriftResult:
    """Automation-safe synchronization drift evidence.

    Selection drift and duplicate ambiguity are synchronization concerns. Missing expected
    parts remain separate validation/preflight evidence and do not make an otherwise
    synchronized work-in-progress project drifted.
    """

    plan: ProjectSyncPlan

    @property
    def in_sync(self) -> bool:
        return not self.plan.changed and self.plan.safe_to_apply

    @property
    def exit_code(self) -> int:
        return 0 if self.in_sync else 2

    def to_dict(self) -> dict[str, object]:
        payload = self.plan.to_dict()
        payload["in_sync"] = self.in_sync
        return payload


def evaluate_project_sync_drift(project: MergeProject) -> ProjectSyncDriftResult:
    """Build synchronization drift evidence without mutating project metadata."""

    return ProjectSyncDriftResult(plan_project_sync(project))
