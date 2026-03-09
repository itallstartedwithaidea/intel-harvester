# Pipeline Architecture

## Data Flow

```
┌─────────────┐
│  domains.txt │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Per Domain Pipeline                                         │
│                                                              │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │ 1. DNS Recon │──▶│ 2. Website   │──▶│ 3. Search       │  │
│  │              │   │    Scraper   │   │    Harvester    │  │
│  │ MX, NS, TXT │   │              │   │                 │  │
│  │ WHOIS, crt  │   │ Sitemap      │   │ DDG, Bing,      │  │
│  │              │   │ Nav/Footer   │   │ Google, GitHub  │  │
│  │ ► emails    │   │ Data attrs   │   │ LinkedIn search │  │
│  │ ► meta      │   │ Schema.org   │   │                 │  │
│  │              │   │ Obfuscated   │   │ ► emails        │  │
│  │              │   │              │   │ ► people        │  │
│  │              │   │ ► emails     │   │                 │  │
│  │              │   │ ► people     │   │                 │  │
│  │              │   │ ► phones     │   │                 │  │
│  └──────┬──────┘   └──────┬───────┘   └────────┬────────┘  │
│         │                 │                     │            │
│         ▼                 ▼                     ▼            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Collected: emails + people               │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ 4. Pattern  │ │ 5. SMTP     │ │ 6. Social   │          │
│  │    Engine   │ │    Verify   │ │   Enricher  │          │
│  │             │ │             │ │             │          │
│  │ Detect:     │ │ RCPT TO    │ │ LinkedIn    │          │
│  │ first.last  │ │ check per  │ │ Twitter/X   │          │
│  │ Generate    │ │ email      │ │ per person  │          │
│  │ candidates  │ │             │ │             │          │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
│         │               │               │                   │
│         ▼               ▼               ▼                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           6b. Ads Transparency (optional)            │    │
│  │     Advertiser ID · Creatives · Platforms · Dates    │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              7. Correlator                            │    │
│  │     Link emails ↔ people ↔ phones ↔ socials          │    │
│  │     Deduplicate · Score confidence · Build records    │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │  contacts.csv        │
              │  intel.json          │
              │  Terminal summary    │
              └──────────────────────┘
```

## Module Responsibilities

| Module | Input | Output | Free? |
|--------|-------|--------|-------|
| `dns_recon.py` | domain | emails, MX provider, nameservers, registrant | ✅ |
| `website_scraper.py` | domain | emails, people (name+title), phones, tech stack | ✅ |
| `search_harvester.py` | domain | emails, people | ✅ |
| `email_pattern.py` | confirmed emails + people | pattern name, generated emails | ✅ |
| `smtp_verifier.py` | email list | verified/rejected per email | ✅ |
| `social_enricher.py` | people list | LinkedIn + Twitter URLs | ✅ |
| `ads_transparency.py` | domain | advertiser info, creatives, platforms | ✅* |
| `utils.py` | — | Logger, RateLimiter, dedup, cleaners | ✅ |

\* Free fallback included. Optional SearchAPI.io key for full data.

## Confidence Scoring

| Score | Meaning |
|-------|---------|
| 100 | SMTP verified — mailbox confirmed to exist |
| 70 | Found publicly — email appeared in search results, website, or DNS |
| 50 | Pattern-generated — created from detected email pattern + person name |
| 10 | SMTP rejected — mailbox does not exist |
| 0 | No email found for this person |
