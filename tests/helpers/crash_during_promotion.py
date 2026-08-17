from __future__ import annotations

import os
import sys
from pathlib import Path

import docmergeforge.utilities.output_transaction as output_transaction
from docmergeforge.utilities.output_transaction import OutputTransaction


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: crash_during_promotion.py OUTPUT_DIR")

    output_dir = Path(sys.argv[1]).resolve()
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
            if destination_path == first_final and source_path == first.staging_path:
                os._exit(97)

        output_transaction.os.replace = replace_then_crash
        transaction.promote()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
