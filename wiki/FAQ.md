# FAQ

## Is this legal?

intel-harvester only accesses publicly available information — the same data you could find by visiting a website, running a Google search, or doing a DNS lookup. It does not bypass authentication, access private systems, or violate any terms of service. That said, always check your local laws regarding data collection and use the tool responsibly.

## Why not just use Apollo or Hunter?

You can. They have larger databases because they've been aggregating for years. But:
- They cost $49-99/month
- Their data can be stale (someone left the company 6 months ago, still in their database)
- They don't offer ads intelligence, tech stack detection, or competitor discovery
- intel-harvester finds data they miss: GitHub commit emails, schema.org structured data, obfuscated emails, data attributes

The best approach is often to use intel-harvester for live scraping and supplement with a paid tool for database lookups when needed.

## I'm getting rate limited by search engines

Increase the delay between requests:
```bash
python harvest.py domains.txt --delay 5
```

For large domain lists (100+), consider running in batches of 20 with breaks between batches.

## SMTP verification says all emails are "None"

This usually means one of:
- The mail server blocks SMTP RCPT TO checks (common with Google Workspace and Microsoft 365)
- The domain has a catch-all configuration (all addresses return 250)
- Your IP or ISP is blocked from connecting to port 25

Try `--skip-smtp` and rely on the pattern engine's confidence scores instead.

## The website scraper isn't finding people

Some sites use JavaScript rendering (React, Angular, Vue SPAs) where the content isn't in the initial HTML. The tool fetches raw HTML, not rendered DOM. For JS-heavy sites, the search engine harvesting step often compensates since Google has already rendered and indexed the content.

## Can I use this for cold email outreach?

The tool finds contact information. How you use it is your responsibility. If sending cold emails, comply with CAN-SPAM (US), CASL (Canada), GDPR (EU), and any applicable anti-spam laws. Always provide an unsubscribe mechanism and identify yourself clearly.

## How do I add a new data source?

See [CONTRIBUTING.md](../CONTRIBUTING.md). Each module follows the same pattern:

```python
class NewModule:
    def __init__(self, domain, config, logger):
        ...
    async def run(self):
        return {"emails": [...], "people": [...]}
```

## What's the SearchAPI.io key for?

It's the only optional paid component. It queries Google Ads Transparency Center for detailed ad intelligence — advertiser IDs, creative counts, platform breakdowns, date ranges. Without it, the ads module still works via a free DuckDuckGo fallback that tells you whether the domain is advertising.

SearchAPI.io has a free tier with limited queries.

## Can I run this on a schedule?

Yes. Wrap it in a cron job:
```bash
0 6 * * 1 cd /path/to/intel-harvester && python harvest.py domains.txt -o weekly_contacts.csv --skip-smtp 2>&1 >> harvest.log
```

## The tool found wrong/outdated information

OSINT data is only as fresh as the source. Websites may not have updated their team pages, DNS records may be stale, and search engine caches can be weeks old. Always verify critical contact information before using it for outreach.
