# Contributing to intel-harvester

Thanks for your interest in contributing. Here's how to get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/intel-harvester.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `pip install -r requirements.txt`
5. Make your changes
6. Test with a real domain: `echo "example.com" | python harvest.py - --verbose`
7. Commit and push
8. Open a Pull Request

## What We Need Help With

### New Data Sources
- Additional search engine modules (Yandex, Baidu for international domains)
- Professional network scrapers beyond LinkedIn
- Public records databases
- SEC/EDGAR filings for public company contacts

### New Output Targets
- Google Sheets integration (read input / write output)
- Airtable export
- HubSpot CRM direct import
- Salesforce export format

### Improvements
- Proxy rotation support for avoiding rate limits
- Async HTTP requests throughout (currently mixed sync/async)
- Better name/title NLP extraction (spaCy integration)
- Catch-all domain detection before SMTP verification
- International email pattern support (non-ASCII characters)

### Documentation
- Wiki pages for each module
- Video walkthrough
- More example use cases

## Code Style

- Python 3.8+ compatible
- Follow existing patterns in the codebase
- Each module should be self-contained with its own class
- All extraction methods should handle errors gracefully (try/except, never crash the pipeline)
- Add debug logging via `self.logger.debug()` for troubleshooting

## Module Structure

Each module follows this pattern:

```python
class ModuleName:
    def __init__(self, domain, config, logger):
        self.domain = domain
        self.config = config
        self.logger = logger

    async def run(self):
        # Do the work
        return {"emails": [...], "people": [...]}
```

## Testing

Test against real domains. The tool is designed for live OSINT, so unit tests with mocked responses only go so far. Always verify with:

```bash
echo "seerinteractive.com" | python harvest.py - --verbose --skip-smtp
```

## Ethics

- Only scrape publicly available information
- Respect robots.txt
- Use reasonable rate limiting (default 2 second delay)
- Don't use this tool for harassment, stalking, or any illegal purpose
- Follow the terms of service of any platforms being queried

## Pull Request Checklist

- [ ] Code follows existing patterns
- [ ] Tested with at least 3 real domains
- [ ] No new paid API dependencies (tool must work free)
- [ ] Error handling doesn't crash the pipeline
- [ ] Debug logging added for new functionality
- [ ] README updated if adding new features
