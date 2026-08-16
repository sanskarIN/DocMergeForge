from __future__ import annotations

from copy import deepcopy
from enum import StrEnum

from docmergeforge.core.models import MergeSettings


class MergeProfile(StrEnum):
    EXACT_PRESERVATION = "Exact Preservation"
    MASTER_EBOOK = "Master eBook"
    PRINT_DRAFT = "Print Draft"
    ARCHIVE = "Archive"
    CUSTOM = "Custom"


def profile_names() -> list[str]:
    return [profile.value for profile in MergeProfile]


def apply_profile(settings: MergeSettings, profile: MergeProfile) -> MergeSettings:
    result = deepcopy(settings)
    result.profile_name = profile.value
    if profile is MergeProfile.EXACT_PRESERVATION:
        result.checksum_generation = True
        result.automatic_validation = True
        result.pdf.add_part_bookmarks = True
        result.docx.start_each_part_on_new_page = False
        result.docx.preserve_sections = True
        result.docx.fidelity_mode = "portable"
    elif profile is MergeProfile.MASTER_EBOOK:
        result.checksum_generation = True
        result.automatic_validation = True
        result.pdf.add_part_bookmarks = True
        result.docx.start_each_part_on_new_page = True
        result.docx.preserve_sections = True
    elif profile is MergeProfile.PRINT_DRAFT:
        result.checksum_generation = True
        result.automatic_validation = True
        result.pdf.add_part_bookmarks = True
        result.docx.start_each_part_on_new_page = True
        result.docx.preserve_sections = False
    elif profile is MergeProfile.ARCHIVE:
        result.checksum_generation = True
        result.automatic_validation = True
        result.pdf.add_part_bookmarks = True
        result.docx.start_each_part_on_new_page = False
        result.docx.preserve_sections = True
    return result
