# Quick Start

## Single Domain

```bash
echo "seerinteractive.com" | python harvest.py - --verbose
```

## Domain List

Create `domains.txt`:
```
seerinteractive.com
hubspot.com
stripe.com
```

Run:
```bash
python harvest.py domains.txt --output contacts.csv --verbose
```

## What Happens

For each domain, the tool runs 7 steps in sequence:

1. **DNS/WHOIS** — identifies email provider, nameservers, registrant, subdomains
2. **Website scraping** — crawls team/about/contact pages for names, titles, emails, phones
3. **Search harvesting** — queries search engines and GitHub for additional emails and people
4. **Pattern detection** — analyzes found emails to detect the naming pattern, generates candidates
5. **SMTP verification** — checks if discovered email addresses actually exist
6. **Social enrichment** — finds LinkedIn and Twitter profiles for discovered contacts
7. **Correlation** — links everything together, deduplicates, scores confidence

Output is a CSV with: domain, name, title, email, phone, email_verified, email_confidence, source, linkedin, twitter

## Speed Expectations

- ~2-3 minutes per domain with all steps enabled
- ~30 seconds per domain with `--skip-smtp --skip-social --skip-ads`
- Rate limiting adds ~2 seconds between requests (configurable with `--delay`)

## First Run Tips

- Start with `--verbose` to see what each step finds
- Use `--skip-smtp` on your first run — SMTP verification is the slowest step
- If search engines start blocking you, increase `--delay` to 5
