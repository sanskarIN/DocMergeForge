from pathlib import Path

import pytest

from docmergeforge.core.exceptions import OutputLockError
from docmergeforge.utilities.output_lock import OutputDirectoryLock
from docmergeforge.utilities.output_transaction import (
    OutputTransaction,
    recover_interrupted_output_transactions,
)


def test_second_output_transaction_is_blocked_while_first_is_active(tmp_path: Path) -> None:
    with OutputTransaction(tmp_path):
        with pytest.raises(OutputLockError, match="already using this output directory"):
            with OutputTransaction(tmp_path):
                pass


def test_recovery_is_blocked_while_publication_lock_is_active(tmp_path: Path) -> None:
    with OutputDirectoryLock(tmp_path):
        with pytest.raises(OutputLockError, match="already using this output directory"):
            recover_interrupted_output_transactions(tmp_path)


def test_recovery_can_run_after_publication_lock_is_released(tmp_path: Path) -> None:
    with OutputDirectoryLock(tmp_path):
        pass

    assert recover_interrupted_output_transactions(tmp_path) == []
