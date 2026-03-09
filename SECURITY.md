# Security Policy

## Responsible Use

intel-harvester is designed for legitimate OSINT research, sales prospecting, and security auditing using publicly available information. It is **not** designed for:

- Unauthorized access to private systems
- Harvesting data behind authentication walls
- Stalking, harassment, or doxing
- Violating any applicable laws or terms of service

## Reporting Vulnerabilities

If you discover a security vulnerability in this tool, please report it by opening a private security advisory on GitHub rather than a public issue.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x     | ✅        |
| 1.x     | ❌        |

## Dependencies

This tool relies on:
- `requests` — HTTP client
- `beautifulsoup4` — HTML parsing
- `dnspython` — DNS queries (optional)
- `tldextract` — Domain parsing (optional)

Keep dependencies updated to avoid known vulnerabilities.
