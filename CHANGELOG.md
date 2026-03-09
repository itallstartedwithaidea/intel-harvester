# Changelog

All notable changes to intel-harvester will be documented in this file.

## [2.0.0] - 2026-03-08

### Added
- **Unified pipeline** combining techniques from theHarvester, EmailHarvester, snscrape, and custom scrapers
- **Enhanced website scraper** with sitemap-first discovery, nav/footer crawling, data-attribute extraction, obfuscated email detection, phone number extraction
- **Domain resolution** testing www/non-www, https/http variants with redirect following
- **Ads transparency module** for Google Ads intelligence via SearchAPI.io (with free fallback)
- **Competitor discovery** for finding other advertisers in the same vertical/region
- **Email pattern engine** supporting 14 naming patterns with auto-detection
- **SMTP verification** via RCPT TO for mailbox existence checking
- **Social enrichment** finding LinkedIn and Twitter profiles via search
- **Phone number extraction** and association with contacts
- **Tech stack detection** for WordPress, Shopify, HubSpot, Next.js, and more
- **Schema.org JSON-LD parsing** for structured Person/Organization data
- **GitHub commit email harvesting** from public repositories
- **Staff directory early stopping** when comprehensive team pages are found
- **CSV and JSON output** with domain metadata
- **GitHub CI/CD** with Python 3.8-3.12 matrix testing

### Architecture
- 8 modules: dns_recon, website_scraper, search_harvester, email_pattern, smtp_verifier, social_enricher, ads_transparency, utils
- Async pipeline with configurable rate limiting
- Zero paid dependencies — all features work without API keys
- Optional SearchAPI.io key for detailed ads transparency data

## [1.0.0] - 2026-03-08

### Added
- Initial release with basic DNS recon, website scraping, email pattern detection, search harvesting, SMTP verification, and social enrichment
