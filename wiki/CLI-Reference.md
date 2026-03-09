# CLI Reference

```
usage: harvest.py [-h] [-o OUTPUT] [-j JSON_OUTPUT] [--skip-dns] [--skip-web]
                  [--skip-search] [--skip-smtp] [--skip-social] [--skip-pattern]
                  [--skip-ads] [--delay DELAY] [--timeout TIMEOUT]
                  [--max-pages MAX_PAGES] [--user-agent USER_AGENT] [-v]
                  [--searchapi-key SEARCHAPI_KEY] [--competitors]
                  [--vertical VERTICAL] [--region REGION]
                  input
```

## Arguments

| Argument | Description |
|----------|-------------|
| `input` | File with domains (one per line) or `-` for stdin |

## Output Options

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Output CSV file path (default: `harvest_TIMESTAMP.csv`) |
| `-j`, `--json-output` | Also output as JSON file |

## Skip Flags

| Flag | Skips | Time Saved |
|------|-------|------------|
| `--skip-dns` | DNS/WHOIS recon | ~5 sec |
| `--skip-web` | Website scraping | ~30 sec |
| `--skip-search` | Search engine harvesting | ~20 sec |
| `--skip-pattern` | Email pattern generation | <1 sec |
| `--skip-smtp` | SMTP email verification | ~30 sec |
| `--skip-social` | LinkedIn/Twitter search | ~20 sec |
| `--skip-ads` | Ads transparency lookup | ~10 sec |

## Performance Options

| Flag | Default | Description |
|------|---------|-------------|
| `--delay` | 2.0 | Seconds between requests |
| `--timeout` | 15 | Request timeout in seconds |
| `--max-pages` | 5 | Max pages to crawl per domain |
| `--user-agent` | Chrome UA | Custom user agent string |
| `-v`, `--verbose` | off | Show detailed step-by-step output |

## Ads Intelligence Options

| Flag | Description |
|------|-------------|
| `--searchapi-key` | SearchAPI.io key (or set `SEARCHAPI_API_KEY` env var) |
| `--competitors` | Also discover competitors |
| `--vertical` | Business vertical for competitor search (e.g. "plumbing") |
| `--region` | Region for competitor search (e.g. "Phoenix, AZ") |

## Examples

```bash
# Basic
python harvest.py domains.txt

# Full output
python harvest.py domains.txt -o contacts.csv -j intel.json -v

# Fast mode
python harvest.py domains.txt --skip-smtp --skip-social --skip-ads -o quick.csv

# With competitor discovery
python harvest.py domains.txt --searchapi-key KEY --competitors --vertical "auto detailing" --region "Barrie, ON"

# Single domain from stdin
echo "example.com" | python harvest.py - -v

# Conservative rate limiting
python harvest.py domains.txt --delay 5 --max-pages 15 --timeout 30
```
