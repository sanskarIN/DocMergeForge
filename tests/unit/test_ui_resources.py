from docmergeforge.ui.resources import (
    BMC_URL,
    BUSINESS_EMAIL,
    BUSINESS_EMAIL_SECONDARY,
    DOCS_URL,
    PAYPAL_URL,
    RAZORPAY_URL,
    REPOSITORY_URL,
    SUPPORT_EMAIL,
    WEBSITE_URL,
)


def test_desktop_support_links_match_canonical_project_values() -> None:
    assert REPOSITORY_URL == "https://github.com/sanskarIN/foliolane"
    assert f"{REPOSITORY_URL}/tree/main/docs" == DOCS_URL
    assert WEBSITE_URL == "https://sanskarin.github.io"
    assert BMC_URL == "https://buymeacoffee.com/SanskarCodes"
    assert RAZORPAY_URL == "https://razorpay.me/@SanskarCodes"
    assert PAYPAL_URL == "https://paypal.me/SanskarCodes"
    assert BUSINESS_EMAIL == "sanskar.businesswork@outlook.com"
    assert BUSINESS_EMAIL_SECONDARY == "sanskar.businesswork@gmail.com"
    assert SUPPORT_EMAIL == "supportramsandesh@gmail.com"
