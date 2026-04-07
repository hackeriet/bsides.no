#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
NO_INDEX = ROOT / "index.html"
EN_INDEX = ROOT / "en" / "index.html"
TIMEOUT_SECONDS = 20
USER_AGENT = "bsides.no freshness checker (+https://bsides.no/)"


@dataclass(frozen=True)
class ChapterCheck:
    slug: str
    title: str
    local_url: str
    no_text: str
    en_text: str
    local_clue_groups: tuple[tuple[str, ...], ...]


CHAPTERS: tuple[ChapterCheck, ...] = (
    ChapterCheck(
        slug="oslo",
        title="BSides Oslo",
        local_url="https://bsidesoslo.no/",
        no_text="29. oktober 2026 · Vulkan Arena",
        en_text="October 29, 2026 · Vulkan Arena",
        local_clue_groups=(
            ("vulkan arena",),
            ("october 29, 2026", "29 october 2026", "29. oktober 2026"),
        ),
    ),
    ChapterCheck(
        slug="kristiansand",
        title="BSides Kristiansand",
        local_url="https://bsideskrs.no/",
        no_text="5. juni 2026 · Noroff i Kristiansand",
        en_text="June 5, 2026 · Noroff in Kristiansand",
        local_clue_groups=(
            ("noroff",),
            ("june 5, 2026", "5 june 2026", "5. juni 2026"),
        ),
    ),
    ChapterCheck(
        slug="bergen",
        title="BSides Bergen",
        local_url="https://bsidesbergen.no/",
        no_text="12. mai 2026 · Vestlandshuset",
        en_text="May 12, 2026 · Vestlandshuset",
        local_clue_groups=(
            ("vestlandshuset",),
            ("may 12, 2026", "12 may 2026", "12. mai 2026"),
        ),
    ),
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).casefold()


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_contains(haystack: str, needle: str, errors: list[str], context: str) -> None:
    if needle not in haystack:
        errors.append(f"{context}: missing `{needle}`")


def assert_any_contains(
    haystack: str,
    needles: Iterable[str],
    errors: list[str],
    context: str,
) -> None:
    if not any(needle in haystack for needle in needles):
        joined = " | ".join(f"`{needle}`" for needle in needles)
        errors.append(f"{context}: missing any of {joined}")


def check_local_pages(errors: list[str]) -> None:
    no_html = load_text(NO_INDEX)
    en_html = load_text(EN_INDEX)

    assert_contains(no_html, 'src="assets-bsides-logo-original-mono.svg"', errors, "index.html")
    assert_contains(en_html, 'src="../assets-bsides-logo-original-mono.svg"', errors, "en/index.html")
    assert_contains(no_html, '<a href="/en/">English</a>', errors, "index.html")
    assert_contains(en_html, '<a href="/">Norsk</a>', errors, "en/index.html")

    for chapter in CHAPTERS:
        assert_contains(
            no_html,
            f'<a class="chapter-link" data-city="{chapter.slug}" href="{chapter.local_url}">',
            errors,
            "index.html",
        )
        assert_contains(no_html, chapter.no_text, errors, f"index.html {chapter.title}")
        assert_contains(en_html, chapter.en_text, errors, f"en/index.html {chapter.title}")
        assert_contains(
            no_html,
            f'<a class="map-point map-point-{chapter.slug}" data-city="{chapter.slug}" href="{chapter.local_url}"',
            errors,
            f"index.html map {chapter.title}",
        )
        assert_contains(
            en_html,
            f'<a class="map-point map-point-{chapter.slug}" data-city="{chapter.slug}" href="{chapter.local_url}"',
            errors,
            f"en/index.html map {chapter.title}",
        )

    stavanger_url = "https://bsides.org/contact/bsides-stavanger/"
    rules_url = "https://bsides.org/rules/"
    assert_contains(no_html, stavanger_url, errors, "index.html Stavanger link")
    assert_contains(en_html, stavanger_url, errors, "en/index.html Stavanger link")
    assert_contains(no_html, rules_url, errors, "index.html rules link")
    assert_contains(en_html, rules_url, errors, "en/index.html rules link")


def check_remote_sources(errors: list[str]) -> None:
    try:
        chapters_page = normalize(fetch_text("https://bsides.org/chapters/"))
    except (HTTPError, URLError) as exc:
        errors.append(f"Failed to fetch https://bsides.org/chapters/: {exc}")
        chapters_page = ""

    if chapters_page:
        for name in (
            "bsides oslo",
            "bsides kristiansand",
            "bsides bergen",
            "bsides stavanger",
        ):
            assert_contains(chapters_page, name, errors, "bsides.org/chapters")

    try:
        stavanger_page = normalize(fetch_text("https://bsides.org/contact/bsides-stavanger/"))
    except (HTTPError, URLError) as exc:
        errors.append(f"Failed to fetch https://bsides.org/contact/bsides-stavanger/: {exc}")
        stavanger_page = ""

    if stavanger_page:
        assert_contains(stavanger_page, "bsides stavanger", errors, "bsides.org/contact/bsides-stavanger")

    try:
        rules_page = normalize(fetch_text("https://bsides.org/rules/"))
    except (HTTPError, URLError) as exc:
        errors.append(f"Failed to fetch https://bsides.org/rules/: {exc}")
        rules_page = ""

    if rules_page:
        assert_any_contains(
            rules_page,
            ("guidelines", "rules", "bsides"),
            errors,
            "bsides.org/rules",
        )

    for chapter in CHAPTERS:
        try:
            page = normalize(fetch_text(chapter.local_url))
        except (HTTPError, URLError) as exc:
            errors.append(f"Failed to fetch {chapter.local_url}: {exc}")
            continue

        assert_contains(page, chapter.title.casefold(), errors, chapter.local_url)
        for group in chapter.local_clue_groups:
            assert_any_contains(page, group, errors, chapter.local_url)


def main() -> int:
    errors: list[str] = []
    check_local_pages(errors)
    check_remote_sources(errors)

    if errors:
        print("Freshness check failed:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Freshness check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
