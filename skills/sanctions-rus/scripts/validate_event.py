#!/usr/bin/env python3
"""Fail-closed validation for sanctions events before publication."""
from __future__ import annotations

import json
import sys
import urllib.parse
from pathlib import Path


BLOCKED_DISCOVERY_HOSTS = (
    "google.com",
    "google.ru",
    "news.google.com",
    "bing.com",
    "msn.com",
    "yandex.ru",
    "yandex.com",
)


def host_matches(host: str, suffix: str) -> bool:
    return host == suffix or host.endswith(f".{suffix}")


def validate_event(event: dict) -> list[str]:
    errors: list[str] = []
    if event.get("structured") is not True:
        errors.append("structured must be true")

    authority = str(event.get("authority_domain") or "").lower().strip().rstrip(".")
    if not authority:
        errors.append("authority_domain is required")

    raw_url = str(event.get("official_url") or "").strip()
    parsed = urllib.parse.urlsplit(raw_url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"} or not host:
        errors.append("official_url must be an absolute HTTP(S) URL")
    else:
        if any(host_matches(host, suffix) for suffix in BLOCKED_DISCOVERY_HOSTS):
            errors.append("official_url must not use a search/news wrapper")
        if authority and not host_matches(host, authority):
            errors.append("official_url host must belong to authority_domain")
        if not parsed.path or parsed.path == "/":
            errors.append("official_url must identify a document or detail page")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_event.py EVENT.json", file=sys.stderr)
        return 2
    event = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    errors = validate_event(event)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("event validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
