#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAIRS = (
    (ROOT / "index.template.html", ROOT / "index.html"),
    (ROOT / "en" / "index.template.html", ROOT / "en" / "index.html"),
    (ROOT / "sitemap.template.xml", ROOT / "sitemap.xml"),
)


def resolve_lastmod_values() -> dict[str, str]:
    source_ref = os.environ.get("LASTMOD_SOURCE_REF", "HEAD")

    try:
        iso_timestamp = subprocess.check_output(
            ["git", "show", "-s", "--format=%cI", source_ref],
            cwd=ROOT,
            text=True,
        ).strip()
        if not iso_timestamp:
            raise ValueError("empty git timestamp")
        parsed = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    except Exception:
        parsed = datetime.now(timezone.utc)
        iso_timestamp = parsed.strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "__LASTMOD_DATE__": parsed.strftime("%Y-%m-%d"),
        "__LASTMOD_ISO__": iso_timestamp.replace("+00:00", "Z"),
    }


def main() -> int:
    replacements = resolve_lastmod_values()

    for source_path, target_path in PAIRS:
        text = source_path.read_text(encoding="utf-8")
        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)
        target_path.write_text(text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
