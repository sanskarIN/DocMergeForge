from __future__ import annotations

from pathlib import Path

from docmergeforge.core.models import DocxSettings, MergeProject, MergeSettings, PdfSettings

PRESET_NAME = "SQL Full Mastery — 120-Part Master Edition"
PDF_FILENAME = "SQL_Full_Mastery_Complete_120_Part_Master_Edition.pdf"
DOCX_FILENAME = "SQL_Full_Mastery_Complete_120_Part_Master_Edition.docx"
MANIFEST_FILENAME = "SQL_Full_Mastery_120_Part_Merge_Manifest.json"
REPORT_HTML_FILENAME = "SQL_Full_Mastery_120_Part_Merge_Report.html"
REPORT_MD_FILENAME = "SQL_Full_Mastery_120_Part_Merge_Report.md"
CHECKSUMS_FILENAME = "SQL_Full_Mastery_120_Part_SHA256SUMS.txt"


def create_sql_full_mastery_project(source: Path, output: Path) -> MergeProject:
    settings = MergeSettings(
        expected_start=1,
        expected_end=120,
        checksum_generation=True,
        automatic_validation=True,
        pdf=PdfSettings(
            add_part_bookmarks=True,
            title="SQL Full Mastery — Complete 120-Part Master Edition",
            author="Ram Sandesh",
            edition="August 2026",
        ),
        docx=DocxSettings(
            start_each_part_on_new_page=True,
            preserve_sections=True,
            fidelity_mode="portable",
        ),
    )
    return MergeProject(
        name=PRESET_NAME,
        source_folders=[source],
        output_folder=output,
        settings=settings,
    )
