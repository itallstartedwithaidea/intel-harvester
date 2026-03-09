# Installation

## Requirements

- Python 3.8 or higher
- `pip` package manager
- Terminal/command line access
- `dig` and `whois` commands (pre-installed on macOS and most Linux distros)

## Install

```bash
git clone https://github.com/itallstartedwithaidea/intel-harvester.git
cd intel-harvester
pip install -r requirements.txt
```

## Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| `requests` | HTTP client for web scraping and API calls | Yes |
| `beautifulsoup4` | HTML parsing for contact extraction | Yes |
| `dnspython` | DNS queries (MX, NS, TXT records) | Optional* |
| `tldextract` | Domain parsing and normalization | Optional* |

\* DNS recon falls back to shell commands (`dig`, `whois`) if these aren't installed.

## Optional: SearchAPI.io Key

The only optional API key. Gets you detailed ads transparency data (advertiser IDs, creative counts, platform breakdowns). Without it, the ads module still works via a free DuckDuckGo fallback.

```bash
export SEARCHAPI_API_KEY=your_key_here
```

## Verify Installation

```bash
python harvest.py --help
```

You should see the full CLI help with all available flags.
