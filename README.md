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
- Avoid official BSides branding assets unless explicit permission is granted

## Main files

- `index.html` - page structure, metadata, structured data, and small interaction scripts
- `styles.css` - visual styling, responsive layout, and interaction states
- `assets-norway-south-base.svg` - source map asset from Wikimedia Commons
- `assets-norway-south-crop-h.svg` - local cropped southern Norway map used by the site
- `LICENSE` - repository license (CC0)

## Licensing

The contents of this repository are released under CC0 unless otherwise noted.

Third-party assets keep their own license terms. In particular, the map asset used on the site
is derived from a Wikimedia Commons file by NordNordWest and must keep its attribution.

## Contributing

Edits are welcome as pull requests.

Useful contributions include:

- correcting event links
- updating event dates or venue text
- improving accessibility
- improving the map or marker placement
- tightening the Norwegian wording

## Notes

- The site currently defaults to Norwegian
- Light and dark mode follow the user’s system preference
- The event list is the primary navigation; the map is secondary
