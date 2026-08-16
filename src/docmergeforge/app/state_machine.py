from __future__ import annotations

from dataclasses import dataclass

from docmergeforge.core.models import MergeState

_ALLOWED: dict[MergeState, set[MergeState]] = {
    MergeState.CREATED: {MergeState.DISCOVERING, MergeState.CANCELLED},
    MergeState.DISCOVERING: {MergeState.VALIDATING, MergeState.FAILED, MergeState.CANCELLED},
    MergeState.VALIDATING: {MergeState.READY, MergeState.FAILED, MergeState.CANCELLED},
    MergeState.READY: {MergeState.MERGING, MergeState.CANCELLED},
    MergeState.MERGING: {MergeState.VERIFYING, MergeState.FAILED, MergeState.CANCELLED},
    MergeState.VERIFYING: {MergeState.REPORTING, MergeState.FAILED, MergeState.CANCELLED},
    MergeState.REPORTING: {MergeState.SUCCEEDED, MergeState.FAILED, MergeState.CANCELLED},
    MergeState.SUCCEEDED: set(),
    MergeState.FAILED: set(),
    MergeState.CANCELLED: set(),
}


@dataclass(slots=True)
class MergeStateMachine:
    state: MergeState = MergeState.CREATED

    def transition(self, target: MergeState) -> None:
        if target not in _ALLOWED[self.state]:
            raise ValueError(f"Illegal merge transition: {self.state} -> {target}")
        self.state = target
