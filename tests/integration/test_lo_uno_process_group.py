import os
import subprocess
import sys
import time

import pytest

from docmergeforge.docx import libreoffice_uno_merge


pytestmark = pytest.mark.skipif(
    os.name != "posix",
    reason="LibreOffice UNO process-group acceptance currently uses POSIX semantics.",
)


def test_process_group_cleanup_reaps_already_exited_launcher() -> None:
    process = subprocess.Popen(
        [sys.executable, "-c", "pass"],
        start_new_session=True,
        text=True,
    )
    time.sleep(0.1)

    libreoffice_uno_merge._terminate_process_group(process)

    assert process.poll() == 0


def test_process_group_cleanup_terminates_isolated_parent_and_child() -> None:
    child_code = "import time; time.sleep(60)"
    parent_code = (
        "import subprocess, sys, time; "
        f"subprocess.Popen([sys.executable, '-c', {child_code!r}]); "
        "time.sleep(60)"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", parent_code],
        start_new_session=True,
        text=True,
    )
    time.sleep(0.2)

    libreoffice_uno_merge._terminate_process_group(process)

    assert process.poll() is not None
    with pytest.raises(ProcessLookupError):
        os.killpg(process.pid, 0)
