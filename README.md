# BSides.no

Static website for finding BSides-related events and chapters in Norway.

## What this repo contains

- A small HTML/CSS site with links to Norwegian BSides events
- A simple map of southern Norway with linked city markers
- No framework, build step, or runtime dependency

## Goals

- Keep the site fast, simple, and easy to maintain
- Make it easy to find Norwegian BSides events from one URL
- Prefer accessibility, readable markup, and useful structure over visual noise
- Use approved BSides branding where explicit permission has been given

## Main files

- `index.html` - Norwegian page structure, metadata, structured data, and small interaction scripts
- `en/index.html` - English version of the same site
- `index.template.html` and `en/index.template.html` - source templates for the published HTML files
- `styles.css` - visual styling, responsive layout, and interaction states
- `assets-bsides-logo-original-mono.svg` - BSides logo used in the page heading
- `assets-hackeriet-logo.svg` - Hackeriet logo used in the site footer
- `favicon-32x32.png`, `apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png` - official BSides icon assets used for browser and app metadata
- `manifest.webmanifest` - web app metadata for browser installability and icon discovery
- `assets-norway-south-base.svg` - source map asset from Wikimedia Commons
- `assets-norway-south-crop-h.svg` - local cropped southern Norway map used by the site
- `scripts/check_sources.py` - scheduled consistency check against chapter sites and BSides Global
- `scripts/render_lastmod.py` - renders machine-facing `lastmod` metadata into the published files
- `.github/workflows/check-content.yml` - daily GitHub Actions job for the freshness check
- `.github/workflows/update-lastmod.yml` - nightly GitHub Actions job that refreshes machine-facing `lastmod` metadata
- `.github/workflows/remind-security-txt-expiry.yml` - opens a reminder issue before `security.txt` expires
- `CNAME` - GitHub Pages custom domain configuration
- `robots.txt` - crawler directives with sitemap reference
- `sitemap.xml` - simple sitemap for the published pages
- `sitemap.template.xml` - source template for the generated sitemap
- `humans.txt` - optional human-facing authorship and site metadata file
- `.well-known/security.txt` and `security.txt` - security contact metadata
- `SECURITY.md` - minimal security reporting guidance
- `404.html` - custom GitHub Pages not-found page
- `LICENSE` - repository license (CC0)

## Licensing

The contents of this repository are released under CC0 unless otherwise noted.

Third-party assets keep their own license terms. In particular, the map asset used on the site
is derived from a Wikimedia Commons file by NordNordWest and must keep its attribution.

The BSides logo and official icon files are not covered by the repository's CC0 license.
They are included for this site based on explicit permission from BSides Global and should be
treated as separate branded assets.

The Hackeriet footer logo is also a separate branded asset and is not part of the repository-wide
CC0 grant.

The custom 404 page uses `hackers-love.jpg`, matching the design used on `hackeriet.no`.
That image should also be treated as a separate asset, not as part of the repository-wide CC0 grant.

## Contributing

Edits are welcome as pull requests.

Useful contributions include:

- correcting event links
- updating event dates or venue text
- improving accessibility
- improving the map or marker placement
- tightening the Norwegian wording
- keeping the Norwegian and English pages in sync

## Notes

- The site currently defaults to Norwegian
- An English version is available at `/en/`
- Light and dark mode follow the user’s system preference
- The event list is the primary navigation; the map is secondary
- GitHub Pages is configured for the `bsides.no` custom domain
- Scheduled automation is confined to off-hours UTC runs and each workflow has a job-level timeout so slow external services do not keep runners busy indefinitely
- A daily GitHub Actions job checks whether the local pages still match the chapter sites and BSides Global listings, opens or updates one issue on failure, and closes it again when the check passes
- A separate nightly job refreshes machine-facing `lastmod` metadata in the published pages and sitemap

## Freshness check

The scheduled checker verifies:

- the Norway-only BSides chapter listing on `bsides.org` still matches the chapters listed on this site
- each chapter still resolves to the expected local or BSides Global page
- each local chapter site still exposes the chapter-specific clues this site relies on
- chapters with events in the next six months also appear on the BSides Global event search for their city
- matching BSides Global event pages have not drifted on title, date, or venue where the local sources expose venue details

The GitHub Actions workflow uses a single `content-drift` label for the automated issue it opens on failure.

Operational safeguards:

- the checker uses a 10-second per-request timeout for upstream HTTP fetches
- the `check-content` workflow has a 10-minute job timeout
- the `update-lastmod` and `remind-security-txt-expiry` workflows have 6-minute job timeouts

## Metadata rendering

- `index.html`, `en/index.html`, and `sitemap.xml` are published artifacts
- `index.template.html`, `en/index.template.html`, and `sitemap.template.xml` keep placeholder values for machine-facing `lastmod` fields
- `scripts/render_lastmod.py` replaces those placeholders using the commit timestamp of the source revision
- `.github/workflows/update-lastmod.yml` runs that renderer once per day during the night (UTC) and can also be triggered manually
- `scripts/render_lastmod.py` uses a 6-second subprocess timeout when resolving the source commit timestamp
- the generated `dateModified`, `og:updated_time`, and sitemap `lastmod` values are meant for search engines, crawlers, and agents, not for visible page text

## Security metadata

- `/.well-known/security.txt` is the canonical security.txt location
- `/security.txt` mirrors the same content for older tooling
- the security contact currently points to GitHub Issues by design; reporters are expected to request private contact there rather than post sensitive details publicly
- a weekly GitHub Actions workflow opens a reminder issue during the last 45 days before the configured `security.txt` expiry date
