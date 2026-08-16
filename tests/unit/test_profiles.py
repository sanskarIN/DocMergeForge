from docmergeforge.core.models import MergeSettings
from docmergeforge.profiles import MergeProfile, apply_profile, profile_names


def test_profile_catalog_contains_required_profiles() -> None:
    assert profile_names() == [
        "Exact Preservation",
        "Master eBook",
        "Print Draft",
        "Archive",
        "Custom",
    ]


def test_master_ebook_profile_does_not_mutate_original_settings() -> None:
    settings = MergeSettings()
    settings.docx.start_each_part_on_new_page = False
    configured = apply_profile(settings, MergeProfile.MASTER_EBOOK)
    assert configured.docx.start_each_part_on_new_page
    assert not settings.docx.start_each_part_on_new_page
