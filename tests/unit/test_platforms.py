from docmergeforge.platforms import current_runtime, support_matrix


def test_support_matrix_covers_desktop_mobile_and_web() -> None:
    targets = {item.id: item for item in support_matrix()}
    assert {
        "windows",
        "macos",
        "linux",
        "android",
        "ios",
        "ipados",
        "chromeos",
        "web",
    } <= set(targets)
    assert targets["windows"].native_desktop
    assert targets["macos"].native_desktop
    assert targets["linux"].native_desktop
    assert targets["android"].web_client
    assert targets["ios"].web_client
    assert not targets["android"].native_desktop


def test_current_runtime_is_privacy_safe_and_structured() -> None:
    payload = current_runtime()
    assert set(payload) == {"platform", "system", "machine", "python"}
    assert isinstance(payload["python"], str)
