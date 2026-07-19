# Security headers

BSides.no is currently served by GitHub Pages. GitHub Pages does not provide a
repository-level way to set arbitrary HTTP response headers for custom policies
such as Content-Security-Policy, Permissions-Policy, or Referrer-Policy.

If the site moves behind a host, CDN, or reverse proxy that supports custom
headers, use this as the baseline:

```http
Content-Security-Policy: default-src 'self'; img-src 'self' https: data:; style-src 'self'; script-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'; upgrade-insecure-requests
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

Notes:

- Only enable HSTS preload after confirming every relevant subdomain is HTTPS-only.
- Keep the CSP restrictive because the site is static and should not need third-party scripts.
- Re-test the site after enabling headers, especially language links, icons, map assets, and footer links.
