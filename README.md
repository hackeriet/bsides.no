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
- `styles.css` - visual styling, responsive layout, and interaction states
- `assets-bsides-logo-original-mono.svg` - BSides logo used in the page heading
- `assets-norway-south-base.svg` - source map asset from Wikimedia Commons
- `assets-norway-south-crop-h.svg` - local cropped southern Norway map used by the site
- `scripts/check_sources.py` - scheduled consistency check against chapter sites and BSides Global
- `.github/workflows/check-content.yml` - daily GitHub Actions job for the freshness check
- `CNAME` - GitHub Pages custom domain configuration
- `LICENSE` - repository license (CC0)

## Licensing

The contents of this repository are released under CC0 unless otherwise noted.

Third-party assets keep their own license terms. In particular, the map asset used on the site
is derived from a Wikimedia Commons file by NordNordWest and must keep its attribution.

The BSides logo is not covered by the repository's CC0 license. It is included for this site
based on explicit permission from BSides Global and should be treated as a separate branded asset.

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
- A daily GitHub Actions job checks whether the local pages still match the chapter sites and BSides Global listings, opens or updates one issue on failure, and closes it again when the check passes
