from __future__ import annotations

import os
import sys
from pathlib import Path

import docmergeforge.utilities.output_transaction as output_transaction
from docmergeforge.utilities.output_transaction import OutputTransaction

CRASH_EXIT_CODES = {
    "after-first-backup": 91,
    "after-first-promotion": 92,
    "after-last-promotion": 93,
}


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[2] not in CRASH_EXIT_CODES:
        options = ", ".join(CRASH_EXIT_CODES)
        raise SystemExit(f"usage: crash_during_promotion.py OUTPUT_DIR {{{options}}}")

    output_dir = Path(sys.argv[1]).resolve()
    crash_point = sys.argv[2]
    first_final = output_dir / "Book.pdf"
    second_final = output_dir / "Merge_Report.md"

    with OutputTransaction(output_dir) as transaction:
        first = transaction.stage(first_final, overwrite=True)
        second = transaction.stage(second_final, overwrite=True)
        first.staging_path.write_bytes(b"new-pdf-publication")
        second.staging_path.write_text("new-report-publication", encoding="utf-8")

        original_replace = output_transaction.os.replace

        def replace_then_crash(source: str | bytes | Path, destination: str | bytes | Path) -> None:
            original_replace(source, destination)
            source_path = Path(source)
            destination_path = Path(destination)

            if (
                crash_point == "after-first-backup"
                and source_path == first_final
                and destination_path.name.startswith("backup-000-")
            ):
                os._exit(CRASH_EXIT_CODES[crash_point])
            if (
                crash_point == "after-first-promotion"
                and source_path == first.staging_path
                and destination_path == first_final
            ):
                os._exit(CRASH_EXIT_CODES[crash_point])
            if (
                crash_point == "after-last-promotion"
                and source_path == second.staging_path
                and destination_path == second_final
            ):
                os._exit(CRASH_EXIT_CODES[crash_point])

        output_transaction.os.replace = replace_then_crash
        transaction.promote()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
