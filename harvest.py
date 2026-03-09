#!/usr/bin/env python3
"""
Domain Harvester — Combined OSINT Contact Intelligence Tool
Chains passive recon, website scraping, email pattern detection,
SMTP verification, and social enrichment into one pipeline.

Usage:
    python harvest.py domains.txt
    python harvest.py domains.txt --output results.csv --verbose
    python harvest.py domains.txt --skip-smtp --skip-social
    echo "seerinteractive.com" | python harvest.py -

Requires: pip install requests beautifulsoup4 dnspython tldextract
Optional: pip install aiosmtplib (for SMTP verification)
"""

import argparse
import asyncio
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from modules.dns_recon import DNSRecon
from modules.website_scraper import WebsiteScraper
from modules.email_pattern import EmailPatternEngine
from modules.search_harvester import SearchHarvester
from modules.smtp_verifier import SMTPVerifier
from modules.social_enricher import SocialEnricher
from modules.ads_transparency import AdsTransparencyModule, CompetitorDiscovery
from modules.utils import Logger, RateLimiter, deduplicate_contacts

BANNER = """
╔═══════════════════════════════════════════════════════╗
║   Domain Harvester v2.0 — Unified OSINT Intelligence  ║
║   Contacts + Ads Transparency + Competitive Intel     ║
║   github.com/itallstartedwithaidea                    ║
╚═══════════════════════════════════════════════════════╝
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Domain Harvester — OSINT Contact Intelligence Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python harvest.py domains.txt
  python harvest.py domains.txt --output contacts.csv
  python harvest.py domains.txt --skip-smtp --skip-social --verbose
  echo "example.com" | python harvest.py -
        """
    )
    parser.add_argument("input", help="File with domains (one per line) or '-' for stdin")
    parser.add_argument("-o", "--output", default=None, help="Output CSV file (default: harvest_YYYYMMDD_HHMMSS.csv)")
    parser.add_argument("-j", "--json-output", default=None, help="Also output as JSON")
    parser.add_argument("--skip-dns", action="store_true", help="Skip DNS/WHOIS recon")
    parser.add_argument("--skip-web", action="store_true", help="Skip website scraping")
    parser.add_argument("--skip-search", action="store_true", help="Skip search engine harvesting")
    parser.add_argument("--skip-smtp", action="store_true", help="Skip SMTP email verification")
    parser.add_argument("--skip-social", action="store_true", help="Skip social media enrichment")
    parser.add_argument("--skip-pattern", action="store_true", help="Skip email pattern generation")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests in seconds (default: 2.0)")
    parser.add_argument("--timeout", type=int, default=15, help="Request timeout in seconds (default: 15)")
    parser.add_argument("--max-pages", type=int, default=5, help="Max pages to crawl per domain (default: 5)")
    parser.add_argument("--user-agent", default=None, help="Custom user agent string")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--searchapi-key", default=None, help="SearchAPI.io key for ads transparency (or set SEARCHAPI_API_KEY env var)")
    parser.add_argument("--skip-ads", action="store_true", help="Skip ads transparency intelligence")
    parser.add_argument("--competitors", action="store_true", help="Also discover competitors (requires searchapi-key)")
    parser.add_argument("--vertical", default=None, help="Business vertical for competitor discovery (e.g. 'auto detailing')")
    parser.add_argument("--region", default=None, help="Region for competitor discovery (e.g. 'Barrie, ON')")
    return parser.parse_args()


def load_domains(input_path):
    """Load domains from file or stdin."""
    domains = []
    if input_path == "-":
        lines = sys.stdin.read().strip().split("\n")
    else:
        if not Path(input_path).exists():
            print(f"[!] File not found: {input_path}")
            sys.exit(1)
        with open(input_path) as f:
            lines = f.read().strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Clean up: remove http(s)://, trailing slashes, www.
        domain = line.replace("https://", "").replace("http://", "").rstrip("/")
        if domain.startswith("www."):
            domain = domain[4:]
        domains.append(domain)

    return list(dict.fromkeys(domains))  # dedupe preserving order


async def harvest_domain(domain, args, logger, rate_limiter):
    """Run the full pipeline for a single domain."""
    logger.header(f"Harvesting: {domain}")
    
    all_contacts = []
    all_emails = set()
    all_people = []
    domain_meta = {
        "domain": domain,
        "mx_provider": None,
        "email_pattern": None,
        "registrant": None,
        "nameservers": [],
        "tech_stack": None,
    }

    config = {
        "delay": args.delay,
        "timeout": args.timeout,
        "max_pages": args.max_pages,
        "user_agent": args.user_agent or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "searchapi_key": args.searchapi_key or os.environ.get("SEARCHAPI_API_KEY"),
        "verbose": args.verbose,
    }

    # ─── STEP 1: DNS & WHOIS Recon ───
    phone_map = {}
    if not args.skip_dns:
        logger.step("Step 1: DNS & WHOIS Recon")
        dns = DNSRecon(domain, config, logger)
        dns_results = await dns.run()
        domain_meta.update(dns_results.get("meta", {}))
        for email in dns_results.get("emails", []):
            all_emails.add(email)
        logger.info(f"  Found {len(dns_results.get('emails', []))} emails, MX: {domain_meta.get('mx_provider', 'unknown')}")
        await rate_limiter.wait()

    # ─── STEP 2: Website Scraping ───
    if not args.skip_web:
        logger.step("Step 2: Website Scraping")
        scraper = WebsiteScraper(domain, config, logger)
        web_results = await scraper.run()
        for email in web_results.get("emails", []):
            all_emails.add(email)
        all_people.extend(web_results.get("people", []))
        if web_results.get("schema_org"):
            domain_meta["tech_stack"] = web_results.get("tech_stack")
        logger.info(f"  Found {len(web_results.get('emails', []))} emails, {len(web_results.get('people', []))} people")
        # Capture phone numbers
        phone_map = web_results.get("phones", {})
        await rate_limiter.wait()

    # ─── STEP 3: Search Engine Harvesting ───
    if not args.skip_search:
        logger.step("Step 3: Search Engine Harvesting")
        harvester = SearchHarvester(domain, config, logger)
        search_results = await harvester.run()
        for email in search_results.get("emails", []):
            all_emails.add(email)
        all_people.extend(search_results.get("people", []))
        logger.info(f"  Found {len(search_results.get('emails', []))} emails, {len(search_results.get('people', []))} people")
        await rate_limiter.wait()

    # ─── STEP 4: Email Pattern Detection & Generation ───
    if not args.skip_pattern:
        logger.step("Step 4: Email Pattern Detection")
        pattern_engine = EmailPatternEngine(domain, list(all_emails), all_people, logger)
        pattern_results = pattern_engine.run()
        domain_meta["email_pattern"] = pattern_results.get("pattern")
        for email in pattern_results.get("generated_emails", []):
            all_emails.add(email)
        logger.info(f"  Pattern: {domain_meta['email_pattern']}, generated {len(pattern_results.get('generated_emails', []))} new emails")

    # ─── STEP 5: SMTP Verification ───
    if not args.skip_smtp:
        logger.step("Step 5: SMTP Verification")
        verifier = SMTPVerifier(domain, list(all_emails), config, logger)
        verified = await verifier.run()
        logger.info(f"  Verified {sum(1 for v in verified.values() if v)} / {len(verified)} emails")
    else:
        verified = {email: None for email in all_emails}

    # ─── STEP 6: Social Enrichment ───
    if not args.skip_social:
        logger.step("Step 6: Social Enrichment")
        enricher = SocialEnricher(domain, all_people, config, logger)
        social_results = await enricher.run()
        logger.info(f"  Enriched {len(social_results)} profiles")
    else:
        social_results = {}

    # ─── STEP 6b: Ads Transparency Intelligence ───
    ads_intel = {}
    if not args.skip_ads:
        logger.step("Step 6b: Ads Transparency Intelligence")
        ads_module = AdsTransparencyModule(domain, config, logger)
        ads_intel = await ads_module.run()
        if ads_intel.get("is_advertising"):
            adv = ads_intel.get("advertiser", {})
            domain_meta["advertising"] = True
            domain_meta["advertiser_name"] = adv.get("name")
            domain_meta["advertiser_id"] = adv.get("id")
            domain_meta["total_creatives"] = ads_intel.get("total_creatives", 0)
            domain_meta["ad_platforms"] = ads_intel.get("platforms", {})
            logger.info(f"  Advertising: YES | Creatives: {ads_intel.get('total_creatives', 0)} | Platforms: {list(ads_intel.get('platforms', {}).keys())}")
        else:
            domain_meta["advertising"] = False
            logger.info(f"  No ad activity found")

    # ─── STEP 6c: Competitor Discovery ───
    competitors = []
    if args.competitors and args.vertical:
        logger.step("Step 6c: Competitor Discovery")
        comp_module = CompetitorDiscovery(domain, args.vertical, args.region or "", config, logger)
        competitors = await comp_module.run()
        domain_meta["competitors"] = competitors
        logger.info(f"  Found {len(competitors)} competitors")

    # ─── STEP 7: Correlate & Build Contacts ───
    logger.step("Step 7: Correlating Results")
    
    # Build contact records
    # First: contacts from people with matched emails
    for person in all_people:
        name = person.get("name", "")
        title = person.get("title", "")
        source = person.get("source", "unknown")
        
        # Try to find a matching email
        email = person.get("email")
        if not email:
            # Check if pattern engine generated one for this person
            name_parts = name.lower().split()
            if len(name_parts) >= 2:
                for e in all_emails:
                    e_lower = e.lower()
                    if name_parts[0] in e_lower or name_parts[-1] in e_lower:
                        email = e
                        break
        
        contact = {
            "domain": domain,
            "name": name,
            "title": title,
            "email": email or "",
            "phone": phone_map.get(email, "") if email else "",
            "email_verified": verified.get(email) if email else None,
            "email_confidence": _confidence_score(email, verified, domain_meta.get("email_pattern")),
            "source": source,
            "linkedin": social_results.get(name, {}).get("linkedin", ""),
            "twitter": social_results.get(name, {}).get("twitter", ""),
        }
        all_contacts.append(contact)

    # Second: orphan emails not linked to any person
    linked_emails = {c["email"] for c in all_contacts if c["email"]}
    for email in all_emails:
        if email not in linked_emails:
            all_contacts.append({
                "domain": domain,
                "name": "",
                "title": "",
                "email": email,
                "phone": phone_map.get(email, ""),
                "email_verified": verified.get(email),
                "email_confidence": _confidence_score(email, verified, domain_meta.get("email_pattern")),
                "source": "passive_recon",
                "linkedin": "",
                "twitter": "",
            })

    # Deduplicate
    all_contacts = deduplicate_contacts(all_contacts)
    
    logger.success(f"  Total contacts for {domain}: {len(all_contacts)}")
    return all_contacts, domain_meta


def _confidence_score(email, verified, pattern):
    """Score email confidence: 100=verified, 80=matches pattern, 50=found publicly, 30=generated."""
    if not email:
        return 0
    if verified.get(email) is True:
        return 100
    if verified.get(email) is False:
        return 10
    # Not verified — score based on source
    return 70  # default: found publicly but not verified


async def main():
    args = parse_args()
    logger = Logger(verbose=args.verbose)
    rate_limiter = RateLimiter(args.delay)

    print(BANNER)

    domains = load_domains(args.input)
    if not domains:
        print("[!] No domains found in input.")
        sys.exit(1)

    logger.info(f"Loaded {len(domains)} domain(s)")
    print()

    all_results = []
    all_meta = []
    
    for i, domain in enumerate(domains, 1):
        logger.info(f"[{i}/{len(domains)}] Processing {domain}")
        try:
            contacts, meta = await harvest_domain(domain, args, logger, rate_limiter)
            all_results.extend(contacts)
            all_meta.append(meta)
        except KeyboardInterrupt:
            logger.warn("\nInterrupted by user. Saving partial results...")
            break
        except Exception as e:
            logger.error(f"Error processing {domain}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            continue
        print()

    # ─── Output ───
    if not all_results:
        logger.warn("No contacts found.")
        return

    # CSV Output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = args.output or f"harvest_{timestamp}.csv"
    
    fieldnames = ["domain", "name", "title", "email", "phone", "email_verified", "email_confidence", "source", "linkedin", "twitter"]
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for contact in all_results:
            writer.writerow(contact)

    logger.success(f"\nResults saved to: {csv_path}")
    logger.info(f"Total contacts: {len(all_results)}")
    logger.info(f"Total domains: {len(all_meta)}")

    # JSON Output
    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "domains_scanned": len(all_meta),
                "total_contacts": len(all_results),
                "domain_meta": all_meta,
                "contacts": all_results,
            }, f, indent=2, default=str)
        logger.success(f"JSON saved to: {args.json_output}")

    # Summary
    print("\n" + "=" * 55)
    print("  HARVEST SUMMARY")
    print("=" * 55)
    for meta in all_meta:
        domain = meta["domain"]
        count = sum(1 for c in all_results if c["domain"] == domain)
        emails = sum(1 for c in all_results if c["domain"] == domain and c["email"])
        pattern = meta.get("email_pattern") or "unknown"
        advertising = "YES" if meta.get("advertising") else "NO"
        creatives = meta.get("total_creatives", 0)
        print(f"  {domain}")
        print(f"    Contacts: {count} | Emails: {emails} | Pattern: {pattern}")
        print(f"    MX: {meta.get('mx_provider', 'unknown')} | NS: {', '.join(meta.get('nameservers', [])[:2])}")
        print(f"    Advertising: {advertising} | Creatives: {creatives}")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
