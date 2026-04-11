#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import socket
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
NO_INDEX = ROOT / "index.html"
EN_INDEX = ROOT / "en" / "index.html"
TIMEOUT_SECONDS = 10
USER_AGENT = "bsides.no freshness checker (+https://bsides.no/)"
TODAY = date.today()
NEAR_FUTURE_DAYS = 183
FETCH_EXCEPTIONS = (HTTPError, URLError, TimeoutError, socket.timeout)


@dataclass(frozen=True)
class ChapterCheck:
    slug: str
    title: str
    city_search: str
    local_url: str
    venue_url: str | None
    no_text: str
    en_text: str
    event_date_iso: str | None
    location_display: str | None
    local_clue_groups: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class Finding:
    category: str
    source: str
    detail: str


CHAPTERS: tuple[ChapterCheck, ...] = (
    ChapterCheck(
        slug="oslo",
        title="BSides Oslo",
        city_search="Oslo",
        local_url="https://bsidesoslo.no/",
        venue_url=None,
        no_text="29. oktober 2026 · Vulkan Arena",
        en_text="October 29, 2026 · Vulkan Arena",
        event_date_iso="2026-10-29",
        location_display="Vulkan Arena",
        local_clue_groups=(
            ("vulkan arena",),
            ("october 29th 2026", "october 29, 2026", "29. oktober 2026"),
        ),
    ),
    ChapterCheck(
        slug="kristiansand",
        title="BSides Kristiansand",
        city_search="Kristiansand",
        local_url="https://bsideskrs.no/",
        venue_url=None,
        no_text="5. juni 2026 · Noroff i Kristiansand",
        en_text="June 5, 2026 · Noroff in Kristiansand",
        event_date_iso="2026-06-05",
        location_display="Noroff",
        local_clue_groups=(
            ("05 june 2026", "5 june 2026", "2026-06-05", "05 juni 2026"),
            ("noroff university college kristiansand campus", "noroff", "location noroff"),
        ),
    ),
    ChapterCheck(
        slug="bergen",
        title="BSides Bergen",
        city_search="Bergen",
        local_url="https://bsidesbergen.no/",
        venue_url=None,
        no_text="12. mai 2026 · Vestlandshuset",
        en_text="May 12, 2026 · Vestlandshuset",
        event_date_iso="2026-05-12",
        location_display="Vestlandshuset",
        local_clue_groups=(
            ("vestlandshuset",),
            ("may 12, 2026", "12 may 2026", "12. mai 2026"),
        ),
    ),
    ChapterCheck(
        slug="stavanger",
        title="BSides Stavanger",
        city_search="Stavanger",
        local_url="https://bsides.org/contact/bsides-stavanger/",
        venue_url=None,
        no_text="Oppføring hos BSides Global",
        en_text="Listed by BSides Global",
        event_date_iso=None,
        location_display=None,
        local_clue_groups=(),
    ),
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).casefold()


def squeeze_spaces(text: str) -> str:
    return re.sub(r"\s+", "", text).casefold()


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add_finding(findings: list[Finding], category: str, source: str, detail: str) -> None:
    findings.append(Finding(category=category, source=source, detail=detail))


def assert_contains(
    haystack: str,
    needle: str,
    findings: list[Finding],
    category: str,
    source: str,
) -> None:
    if needle not in haystack:
        add_finding(findings, category, source, f"Missing `{needle}`")


def assert_any_contains(
    haystack: str,
    needles: Iterable[str],
    findings: list[Finding],
    category: str,
    source: str,
) -> None:
    if not any(needle in haystack for needle in needles):
        joined = " | ".join(f"`{needle}`" for needle in needles)
        add_finding(findings, category, source, f"Missing any of {joined}")


def extract_json_ld(html: str) -> list[object]:
    matches = re.findall(
        r'<script[^>]+type="application/ld\+json"[^>]*>\s*(.*?)\s*</script>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )
    parsed: list[object] = []
    for raw in matches:
        try:
            parsed.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return parsed


def iter_events_from_json_ld(html: str) -> list[dict]:
    events: list[dict] = []
    for obj in extract_json_ld(html):
        if isinstance(obj, dict):
            if obj.get("@type") == "Event":
                events.append(obj)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict) and item.get("@type") == "Event":
                    events.append(item)
    return events


def parse_event_date(date_text: str | None) -> date | None:
    if not date_text:
        return None
    try:
        return datetime.fromisoformat(date_text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def is_near_future(chapter: ChapterCheck) -> bool:
    if not chapter.event_date_iso:
        return False
    event_day = parse_event_date(chapter.event_date_iso)
    if not event_day:
        return False
    delta = (event_day - TODAY).days
    return 0 <= delta <= NEAR_FUTURE_DAYS


def search_results_url(chapter: ChapterCheck) -> str:
    return f"https://bsides.org/events/list/?tribe-bar-search={chapter.city_search}"


def extract_norway_chapter_names(chapters_html: str) -> set[str]:
    names = {
        match.strip()
        for match in re.findall(
            r'contact-list-card-last_name-value">([^<]+)</div>',
            chapters_html,
            flags=re.IGNORECASE,
        )
        if match.strip().startswith("BSides ")
    }
    return names


def check_local_pages(findings: list[Finding]) -> None:
    no_html = load_text(NO_INDEX)
    en_html = load_text(EN_INDEX)

    assert_contains(
        no_html,
        'src="assets-bsides-logo-original-mono.svg"',
        findings,
        "Local pages",
        "index.html",
    )
    assert_contains(
        en_html,
        'src="../assets-bsides-logo-original-mono.svg"',
        findings,
        "Local pages",
        "en/index.html",
    )
    assert_contains(no_html, '<a href="/en/">English</a>', findings, "Local pages", "index.html")
    assert_contains(en_html, '<a href="/">Norsk</a>', findings, "Local pages", "en/index.html")

    for chapter in CHAPTERS:
        assert_contains(
            no_html,
            f'<a class="chapter-link" data-city="{chapter.slug}" href="{chapter.local_url}">',
            findings,
            "Local pages",
            "index.html",
        )
        assert_contains(no_html, chapter.no_text, findings, "Local pages", f"index.html {chapter.title}")
        assert_contains(en_html, chapter.en_text, findings, "Local pages", f"en/index.html {chapter.title}")
        assert_contains(
            no_html,
            f'<a class="map-point map-point-{chapter.slug}" data-city="{chapter.slug}" href="{chapter.local_url}"',
            findings,
            "Local pages",
            f"index.html map {chapter.title}",
        )
        assert_contains(
            en_html,
            f'<a class="map-point map-point-{chapter.slug}" data-city="{chapter.slug}" href="{chapter.local_url}"',
            findings,
            "Local pages",
            f"en/index.html map {chapter.title}",
        )

    rules_url = "https://bsides.org/rules/"
    assert_contains(no_html, rules_url, findings, "Local pages", "index.html rules link")
    assert_contains(en_html, rules_url, findings, "Local pages", "en/index.html rules link")


def check_norway_chapters(findings: list[Finding]) -> None:
    url = "https://bsides.org/chapters/?cl_1=Norway&cl_2="
    try:
        html = fetch_text(url)
    except FETCH_EXCEPTIONS as exc:
        add_finding(findings, "Norway chapter listing", url, f"Fetch failed: {exc}")
        return

    found = extract_norway_chapter_names(html)
    expected = {chapter.title for chapter in CHAPTERS}

    missing = sorted(expected - found)
    extra = sorted(found - expected)

    for name in missing:
        add_finding(findings, "Norway chapter listing", url, f"Missing Norway chapter `{name}`")
    for name in extra:
        add_finding(findings, "Norway chapter listing", url, f"Unexpected Norway chapter `{name}`")


def check_rules_page(findings: list[Finding]) -> None:
    url = "https://bsides.org/rules/"
    try:
        rules_page = normalize(fetch_text(url))
    except FETCH_EXCEPTIONS as exc:
        add_finding(findings, "BSides Global rules", url, f"Fetch failed: {exc}")
        return

    assert_any_contains(
        rules_page,
        ("guidelines", "rules", "bsides"),
        findings,
        "BSides Global rules",
        url,
    )


def compare_global_event_page(
    chapter: ChapterCheck,
    event_url: str,
    local_sources: str,
    findings: list[Finding],
) -> None:
    try:
        event_html = fetch_text(event_url)
    except FETCH_EXCEPTIONS as exc:
        add_finding(findings, "BSides Global event page", event_url, f"Fetch failed: {exc}")
        return

    event_page = normalize(event_html)
    compact_event_page = squeeze_spaces(event_html)
    compact_title = squeeze_spaces(chapter.title)

    if compact_title not in compact_event_page:
        add_finding(
            findings,
            "BSides Global event page",
            event_url,
            f"Missing chapter title `{chapter.title}`",
        )

    if chapter.event_date_iso:
        assert_contains(
            event_page,
            chapter.event_date_iso,
            findings,
            "BSides Global event page",
            event_url,
        )

    if chapter.location_display:
        local_has_location = chapter.location_display.casefold() in local_sources
        global_has_location = chapter.location_display.casefold() in event_page
        if local_has_location and not global_has_location:
            add_finding(
                findings,
                "BSides Global event page",
                event_url,
                f"Missing location clue `{chapter.location_display}` that exists on the local source",
            )


def check_local_and_global_event_state(chapter: ChapterCheck, findings: list[Finding]) -> None:
    try:
        local_html = fetch_text(chapter.local_url)
    except FETCH_EXCEPTIONS as exc:
        add_finding(findings, "Local chapter site", chapter.local_url, f"Fetch failed: {exc}")
        return

    local_page = normalize(local_html)
    compact_local = squeeze_spaces(local_html)
    compact_title = squeeze_spaces(chapter.title)
    local_sources = local_page

    if chapter.venue_url:
        try:
            venue_html = fetch_text(chapter.venue_url)
        except FETCH_EXCEPTIONS as exc:
            add_finding(findings, "Local venue page", chapter.venue_url, f"Fetch failed: {exc}")
        else:
            local_sources = f"{local_sources} {normalize(venue_html)}"

    if compact_title not in compact_local:
        add_finding(
            findings,
            "Local chapter site",
            chapter.local_url,
            f"Missing chapter title `{chapter.title}`",
        )

    for group in chapter.local_clue_groups:
        assert_any_contains(
            local_page,
            group,
            findings,
            "Local chapter site",
            chapter.local_url,
        )

    if not is_near_future(chapter):
        return

    results_url = search_results_url(chapter)
    try:
        results_html = fetch_text(results_url)
    except FETCH_EXCEPTIONS as exc:
        add_finding(findings, "BSides Global event search", results_url, f"Fetch failed: {exc}")
        return

    events = iter_events_from_json_ld(results_html)
    if not events:
        add_finding(
            findings,
            "BSides Global event search",
            results_url,
            f"No BSides Global event found for near-future local event `{chapter.title}`",
        )
        return

    matching_event: dict | None = None
    for event in events:
        name = squeeze_spaces(str(event.get("name", "")))
        start_date = str(event.get("startDate", ""))
        if compact_title in name and chapter.event_date_iso and start_date.startswith(chapter.event_date_iso):
            matching_event = event
            break

    if matching_event is None:
        add_finding(
            findings,
            "BSides Global event search",
            results_url,
            f"No matching BSides Global event found for `{chapter.title}` on `{chapter.event_date_iso}`",
        )
        return

    event_url = matching_event.get("url")
    if isinstance(event_url, str) and event_url:
        compare_global_event_page(chapter, event_url, local_sources, findings)


def render_findings_markdown(findings: list[Finding]) -> str:
    grouped: dict[str, list[Finding]] = {}
    for finding in findings:
        grouped.setdefault(finding.category, []).append(finding)

    lines = [
        "# Freshness check failed",
        "",
        f"- Findings: `{len(findings)}`",
        f"- Categories: `{len(grouped)}`",
        "",
        "## Findings",
        "",
    ]

    for category in sorted(grouped):
        lines.append(f"### {category}")
        lines.append("")
        for finding in grouped[category]:
            lines.append(f"- Source: `{finding.source}`")
            lines.append(f"  Problem: {finding.detail}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    findings: list[Finding] = []
    check_local_pages(findings)
    check_norway_chapters(findings)
    check_rules_page(findings)

    for chapter in CHAPTERS:
        check_local_and_global_event_state(chapter, findings)

    if findings:
        print(render_findings_markdown(findings), end="")
        return 1

    print("Freshness check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
