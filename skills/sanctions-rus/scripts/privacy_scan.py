#!/usr/bin/env python3
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".txt", ".service", ".timer"}
PATTERNS = {
    "secret": re.compile(r"(?:github_pat_|ghp_|bot\d{5,}:)[A-Za-z0-9_-]+", re.I),
    "absolute-home-path": re.compile(r"/(?:root|home)/[^\s'\"]+"),
    "telegram-numeric-id": re.compile(r"(?<!\d)-100\d{8,}|(?<!\d)\d{9,}(?!\d)"),
    "private-config": re.compile(r"(?:chat_id|channel_id)[\"']?\s*[:=]\s*[\"'](?:@[-\w]+|-?\d{7,})[\"']", re.I),
}


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    findings = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                if "channel_id\": null" in match.group(0).lower():
                    continue
                findings.append(f"{path.relative_to(root)}: {name}")
    if findings:
        print("\n".join(sorted(set(findings))))
        raise SystemExit(1)
    print("Privacy scan passed")


if __name__ == "__main__":
    main()
