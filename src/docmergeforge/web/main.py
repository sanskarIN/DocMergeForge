from __future__ import annotations

import argparse
import os
import secrets
from ipaddress import ip_address


def is_loopback_host(host: str) -> bool:
    """Return whether a bind host is loopback-only."""

    normalized = host.strip().casefold()
    if normalized == "localhost":
        return True
    try:
        return ip_address(normalized).is_loopback
    except ValueError:
        return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docmergeforge-web",
        description="Run the responsive DocMergeForge browser interface.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument(
        "--token",
        default=os.environ.get("DOCMERGEFORGE_WEB_TOKEN"),
        help="Access token required for merge requests. Required for non-loopback binds.",
    )
    parser.add_argument(
        "--max-upload-mib",
        default=4096,
        type=int,
        help="Maximum total upload size per merge request in MiB.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not (1 <= args.port <= 65535):
        parser.error("--port must be between 1 and 65535.")
    if args.max_upload_mib < 1:
        parser.error("--max-upload-mib must be at least 1.")
    if not is_loopback_host(args.host) and not args.token:
        parser.error(
            "A non-loopback bind requires --token or DOCMERGEFORGE_WEB_TOKEN. "
            "This prevents an unauthenticated LAN merge service."
        )

    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit(
            'Web dependencies are not installed. Run: pip install -e ".[web]"'
        ) from exc

    from docmergeforge.web.app import create_app

    token = args.token
    if token == "auto":
        token = secrets.token_urlsafe(24)
        print(f"Generated access token: {token}")

    app = create_app(
        access_token=token,
        max_upload_bytes=args.max_upload_mib * 1024 * 1024,
    )
    if args.host in {"0.0.0.0", "::"}:
        print(f"DocMergeForge Web listening on all interfaces at port {args.port}.")
        print(f"On this computer: http://127.0.0.1:{args.port}/")
        print(f"On another device: http://<this-computer-LAN-IP>:{args.port}/")
    else:
        print(f"DocMergeForge Web: http://{args.host}:{args.port}/")
    if token:
        print("Merge API access token is enabled.")
        print("Enter it in the browser's 'Access token (LAN only)' field.")
        print("For a trusted one-time link use #token=<token>; never use ?token=<token>.")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
