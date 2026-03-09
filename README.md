# intel-harvester

**Free, open-source OSINT domain intelligence tool.** Extract contacts, emails, phone numbers, job titles, social profiles, and advertising intelligence from any domain — no paid API keys required.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/itallstartedwithaidea/intel-harvester.svg?style=social)](https://github.com/itallstartedwithaidea/intel-harvester)

> Built by a practitioner managing $350M+ in ad spend. Combines the best techniques from [theHarvester](https://github.com/laramies/theHarvester), [EmailHarvester](https://github.com/maldevel/EmailHarvester), and [snscrape](https://github.com/JustAnotherArchivist/snscrape) into one unified pipeline — plus website crawling, ads transparency, and email pattern detection that none of them offer.

---

## What It Does

Feed it a domain. Get back everything.

```
$ python harvest.py domains.txt --verbose

══════ Harvesting: jamesdean.com ══════
  ► Step 1: DNS & WHOIS Recon
    Found 3 emails, MX: Google Workspace
  ► Step 2: Website Scraping
    Found 8 emails, 14 people
  ► Step 3: Search Engine Harvesting
    Found 5 emails, 7 people
  ► Step 4: Email Pattern Detection
    Pattern: first.last, generated 9 new emails
  ► Step 5: SMTP Verification
    Verified 12 / 16 emails
  ► Step 6: Social Enrichment
    Enriched 8 profiles
  ► Step 6b: Ads Transparency Intelligence
    Advertising: YES | Creatives: 23 | Platforms: ['Search', 'Display']
  ► Step 7: Correlating Results
  ✓ Total contacts: 21
```

### Output (CSV)

| domain | name | title | email | phone | email_verified | confidence | source | linkedin | twitter |
|--------|------|-------|-------|-------|---------------|------------|--------|----------|---------|
| jamesdean.com | John Smith | VP of Sales | john.smith@jamesdeas. | (215) 555-0123 | True | 100 | website:/team | linkedin.com/in/... | x.com/... |

---

## Quick Start

```bash
git clone https://github.com/itallstartedwithaidea/intel-harvester.git
cd intel-harvester
pip install -r requirements.txt

# Single domain
echo "example.com" | python harvest.py - --verbose

# Domain list
python harvest.py domains.txt --output contacts.csv

# Full intelligence + JSON
python harvest.py domains.txt -o contacts.csv --json-output intel.json -v
```

---

## The Pipeline — 8 Modules, All Free

### 1. DNS & WHOIS Recon
Identifies email provider (Google Workspace, Microsoft 365, Zoho), nameservers, hosting provider, registrant info, connected services from TXT/SPF records, and subdomains from certificate transparency logs (crt.sh).

### 2. Website Scraping (Enhanced)
Goes beyond basic crawling with techniques from production-grade scrapers:
- **Sitemap-first discovery** — parses XML/TXT sitemaps before falling back to common paths
- **Robots.txt mining** — extracts additional sitemap references
- **Navigation + footer crawling** — scans nav, header, menu, and footer elements for team page links
- **Domain resolution** — tests www/non-www, https/http variants and follows redirects
- **Data attribute extraction** — pulls `data-email`, `data-staff-name`, `data-title` from HTML elements
- **Obfuscated email detection** — catches `name [at] company [dot] com` patterns
- **Phone number extraction** — finds phone numbers and associates them with nearby contacts
- **Schema.org parsing** — reads JSON-LD structured data for Person/Organization
- **Staff card detection** — matches team card CSS patterns to extract name + title pairs
- **Tech stack detection** — identifies WordPress, Shopify, HubSpot, Next.js, and more
- **Early stopping** — recognizes comprehensive staff directories and stops crawling

### 3. Search Engine Harvesting
Queries DuckDuckGo, Bing, and Google for `"@domain.com"` email references. Searches GitHub commit history for developer emails. Searches LinkedIn via DuckDuckGo for people at the company with names and titles.

### 4. Email Pattern Detection
Analyzes confirmed emails to auto-detect the company's naming convention. Supports 14 patterns:

`first.last` · `firstlast` · `first_last` · `flast` · `firstl` · `f.last` · `first` · `last.first` · `lastf` · `last` · `last_first` · `first.l` · `fl`

Generates candidate emails for every person found without one.

### 5. SMTP Verification
Connects to the MX server and issues `RCPT TO` commands to check if a mailbox actually exists — without sending any email. Returns verified (100), pattern-generated (70), or rejected (10) confidence scores.

### 6. Social Enrichment
Searches DuckDuckGo for LinkedIn and Twitter/X profiles matching discovered contacts. Links profiles to contact records.

### 7. Ads Transparency Intelligence *(optional)*
Discovers if the domain is running Google Ads. Identifies the advertiser, collects ad creatives, breaks down by platform (Search, Display, YouTube) and date range. Free fallback included — optional SearchAPI.io key for full creative data.

### 8. Competitor Discovery *(optional)*
Finds other companies advertising in the same vertical and region. Returns competitor domains, advertiser names, and IDs.

---

## Advanced Usage

```bash
# Skip slow steps for fast results
python harvest.py domains.txt --skip-smtp --skip-social --skip-ads

# Ads intelligence (optional — free SearchAPI.io key)
export SEARCHAPI_API_KEY=your_key
python harvest.py domains.txt -v

# Competitor discovery
python harvest.py domains.txt --competitors --vertical "plumbing" --region "Phoenix, AZ"

# Slower requests to avoid rate limiting
python harvest.py domains.txt --delay 5 --max-pages 15

# Pipe from stdin
cat my_domains.txt | python harvest.py - -o results.csv
```

---

## How It Compares

| Feature | intel-harvester | theHarvester | EmailHarvester | Apollo ($49/mo) | Hunter ($49/mo) |
|---------|:---:|:---:|:---:|:---:|:---:|
| Email discovery | ✅ | ✅ | ✅ | ✅ | ✅ |
| Names + titles | ✅ | ⚠️ limited | ❌ | ✅ | ❌ |
| Phone numbers | ✅ | ❌ | ❌ | ✅ | ❌ |
| Email pattern detection | ✅ | ❌ | ❌ | ❌ | ✅ |
| SMTP verification | ✅ | ❌ | ❌ | ✅ | ✅ |
| Sitemap discovery | ✅ | ❌ | ❌ | ❌ | ❌ |
| Data attribute scraping | ✅ | ❌ | ❌ | ❌ | ❌ |
| Obfuscated emails | ✅ | ❌ | ❌ | ❌ | ❌ |
| Schema.org parsing | ✅ | ❌ | ❌ | ❌ | ❌ |
| LinkedIn search | ✅ | ✅ | ⚠️ broken | ✅ | ❌ |
| GitHub emails | ✅ | ✅ | ❌ | ❌ | ❌ |
| DNS/WHOIS | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ads intelligence | ✅ | ❌ | ❌ | ❌ | ❌ |
| Competitor discovery | ✅ | ❌ | ❌ | ❌ | ❌ |
| Tech stack detection | ✅ | ❌ | ❌ | ❌ | ❌ |
| Cost | **Free** | Free* | Free | $49-99/mo | $49/mo |

\* theHarvester's best modules require paid API keys (Shodan, Hunter, SecurityTrails)

---

## Use Cases

- **Sales prospecting** — find decision makers and their direct emails at target companies
- **Competitive intelligence** — discover what ads competitors are running, on which platforms, and for how long
- **Market research** — map organizational structures from company websites
- **Lead generation** — build prospect lists with verified contact info from any domain list
- **Agency new business** — combine contact intelligence with ad transparency data for relevant outreach
- **Security auditing** — discover exposed emails, subdomains, and connected services

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Issues and PRs welcome.

---

## License

MIT License — See [LICENSE](LICENSE) for details.

---

**Built by [@itallstartedwithaidea](https://github.com/itallstartedwithaidea)** — Practitioner-built tools for people who do the work.
