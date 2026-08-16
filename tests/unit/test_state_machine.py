import pytest

from docmergeforge.app.state_machine import MergeStateMachine
from docmergeforge.core.models import MergeState


def test_happy_path() -> None:
    machine = MergeStateMachine()
    for state in [
        MergeState.DISCOVERING,
        MergeState.VALIDATING,
        MergeState.READY,
        MergeState.MERGING,
        MergeState.VERIFYING,
        MergeState.REPORTING,
        MergeState.SUCCEEDED,
    ]:
        machine.transition(state)
    assert machine.state is MergeState.SUCCEEDED


def test_cannot_skip_validation() -> None:
    machine = MergeStateMachine()
    with pytest.raises(ValueError):
        machine.transition(MergeState.MERGING)
