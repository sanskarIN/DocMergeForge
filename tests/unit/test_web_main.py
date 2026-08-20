from docmergeforge.web.main import build_parser, is_loopback_host


def test_loopback_host_detection() -> None:
    assert is_loopback_host("127.0.0.1")
    assert is_loopback_host("::1")
    assert is_loopback_host("localhost")
    assert not is_loopback_host("0.0.0.0")
    assert not is_loopback_host("192.168.1.10")


def test_web_parser_defaults_to_loopback() -> None:
    args = build_parser().parse_args([])
    assert args.host == "127.0.0.1"
    assert args.port == 8765
    assert args.max_upload_mib == 4096
