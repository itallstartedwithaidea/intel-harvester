"""Ads Transparency intelligence module.
Discovers what ads a domain is running via Google Ads Transparency Center.
Uses SearchAPI.io as the primary data provider (or falls back to direct scraping).

Provides:
- Advertiser identification (who owns the ads)
- Creative collection (what ads are running)
- Platform/format breakdown (Search, Display, YouTube, etc.)
- Time range analysis (how long ads have been running)
- Competitive intelligence (who else is advertising for similar terms)
"""

import asyncio
import json
import re
from urllib.parse import quote

import requests

from modules.utils import Logger


class AdsTransparencyModule:
    """Query Google Ads Transparency Center for ad intelligence on a domain."""

    def __init__(self, domain, config, logger):
        self.domain = domain
        self.config = config
        self.logger = logger
        self.searchapi_key = config.get("searchapi_key") or None
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.get("user_agent", "Mozilla/5.0"),
        })

    async def run(self):
        """Run ads transparency discovery for the domain."""
        results = {
            "advertiser": None,
            "creatives": [],
            "platforms": {},
            "date_range": {"first_seen": None, "last_seen": None},
            "total_creatives": 0,
            "is_advertising": False,
        }

        if self.searchapi_key:
            results = await self._searchapi_lookup(results)
        else:
            results = await self._free_lookup(results)

        return results

    async def _searchapi_lookup(self, results):
        """Use SearchAPI.io to query Google Ads Transparency Center."""
        try:
            # Step 1: Search for the advertiser by domain
            url = "https://www.searchapi.io/api/v1/search"
            params = {
                "engine": "google_ads_transparency_center",
                "advertiser_query": self.domain,
                "api_key": self.searchapi_key,
            }
            resp = self.session.get(url, params=params, timeout=self.config.get("timeout", 15))

            if resp.status_code != 200:
                self.logger.debug(f"  SearchAPI returned {resp.status_code}")
                return results

            data = resp.json()
            advertisers = data.get("advertiser_pages", []) or data.get("advertisers", [])

            if not advertisers:
                self.logger.debug(f"  No advertisers found for {self.domain}")
                return results

            # Take the best match
            best = None
            for adv in advertisers:
                adv_domain = (adv.get("domain") or "").lower()
                adv_name = (adv.get("name") or adv.get("advertiser_name") or "").lower()
                if self.domain.lower() in adv_domain or self.domain.lower().split(".")[0] in adv_name:
                    best = adv
                    break
            if not best and advertisers:
                best = advertisers[0]

            if best:
                results["advertiser"] = {
                    "id": best.get("advertiser_id") or best.get("id"),
                    "name": best.get("name") or best.get("advertiser_name"),
                    "domain": best.get("domain"),
                    "region": best.get("region"),
                    "verification_status": best.get("verification_status"),
                }
                results["is_advertising"] = True

                # Step 2: Get creatives for this advertiser
                adv_id = results["advertiser"]["id"]
                if adv_id:
                    await self._fetch_creatives(adv_id, results)

            return results

        except Exception as e:
            self.logger.debug(f"  SearchAPI lookup failed: {e}")
            return results

    async def _fetch_creatives(self, advertiser_id, results):
        """Fetch ad creatives for a specific advertiser."""
        try:
            url = "https://www.searchapi.io/api/v1/search"
            params = {
                "engine": "google_ads_transparency_center",
                "advertiser_id": advertiser_id,
                "api_key": self.searchapi_key,
            }

            # Fetch up to 3 pages of creatives
            for page in range(3):
                resp = self.session.get(url, params=params, timeout=self.config.get("timeout", 15))
                if resp.status_code != 200:
                    break

                data = resp.json()
                creatives = data.get("ad_creatives", []) or data.get("creatives", [])

                for creative in creatives:
                    creative_record = {
                        "creative_id": creative.get("creative_id") or creative.get("id"),
                        "format": creative.get("format") or creative.get("ad_format"),
                        "platform": creative.get("platform"),
                        "first_shown": creative.get("first_shown") or creative.get("first_shown_datetime"),
                        "last_shown": creative.get("last_shown") or creative.get("last_shown_datetime"),
                        "days_shown": creative.get("total_days_shown"),
                        "target_domain": creative.get("target_domain") or creative.get("domain"),
                        "details_link": creative.get("details_link") or creative.get("link"),
                    }
                    results["creatives"].append(creative_record)

                    # Track platform breakdown
                    platform = creative_record["platform"] or "unknown"
                    results["platforms"][platform] = results["platforms"].get(platform, 0) + 1

                    # Track date range
                    for date_field in ["first_shown", "last_shown"]:
                        date_val = creative_record.get(date_field)
                        if date_val:
                            if not results["date_range"]["first_seen"] or date_val < results["date_range"]["first_seen"]:
                                results["date_range"]["first_seen"] = date_val
                            if not results["date_range"]["last_seen"] or date_val > results["date_range"]["last_seen"]:
                                results["date_range"]["last_seen"] = date_val

                # Check for next page
                next_token = data.get("next_page_token") or data.get("serpapi_pagination", {}).get("next_page_token")
                if not next_token:
                    break
                params["page_token"] = next_token
                await asyncio.sleep(1)

            results["total_creatives"] = len(results["creatives"])

        except Exception as e:
            self.logger.debug(f"  Creative fetch failed: {e}")

    async def _free_lookup(self, results):
        """Free fallback — use DuckDuckGo to find ads transparency info."""
        try:
            # Search for the domain on Google Ads Transparency Center
            query = f'site:adstransparency.google.com "{self.domain}"'
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            resp = self.session.get(url, timeout=self.config.get("timeout", 15))

            if resp.status_code == 200:
                # Look for transparency center links
                links = re.findall(
                    r'adstransparency\.google\.com/advertiser/([A-Z0-9]+)',
                    resp.text
                )
                if links:
                    results["advertiser"] = {
                        "id": links[0],
                        "name": None,
                        "domain": self.domain,
                        "region": None,
                        "verification_status": None,
                        "transparency_url": f"https://adstransparency.google.com/advertiser/{links[0]}",
                    }
                    results["is_advertising"] = True
                    self.logger.debug(f"  Found transparency ID: {links[0]}")

            # Also search for recent ad activity mentions
            query2 = f'"{self.domain}" google ads advertising 2026'
            url2 = f"https://html.duckduckgo.com/html/?q={quote(query2)}"
            resp2 = self.session.get(url2, timeout=self.config.get("timeout", 15))
            if resp2.status_code == 200:
                # Extract any mentions of ad platforms
                text = resp2.text.lower()
                platforms_found = []
                for platform in ["google ads", "meta ads", "facebook ads", "microsoft ads", "bing ads",
                                "linkedin ads", "youtube ads", "display ads", "search ads"]:
                    if platform in text:
                        platforms_found.append(platform)
                if platforms_found:
                    results["platforms_mentioned"] = platforms_found

        except Exception as e:
            self.logger.debug(f"  Free lookup failed: {e}")

        return results


class CompetitorDiscovery:
    """Discover competitors advertising for the same keywords/verticals."""

    def __init__(self, domain, vertical, region, config, logger):
        self.domain = domain
        self.vertical = vertical
        self.region = region
        self.config = config
        self.logger = logger
        self.searchapi_key = config.get("searchapi_key")
        self.session = requests.Session()

    async def run(self):
        """Find competitors advertising in the same space."""
        competitors = []

        if not self.searchapi_key:
            self.logger.debug("  No SearchAPI key — skipping competitor discovery")
            return competitors

        try:
            # Search for advertisers in the same vertical + region
            queries = [
                f"{self.vertical} {self.region}",
                f"{self.vertical} near me",
            ]

            seen_domains = {self.domain.lower()}

            for query in queries:
                url = "https://www.searchapi.io/api/v1/search"
                params = {
                    "engine": "google_ads_transparency_center",
                    "advertiser_query": query,
                    "region": "US",
                    "api_key": self.searchapi_key,
                }
                resp = self.session.get(url, params=params, timeout=self.config.get("timeout", 15))
                if resp.status_code != 200:
                    continue

                data = resp.json()
                for adv in data.get("advertiser_pages", []) or data.get("advertisers", []):
                    adv_domain = (adv.get("domain") or "").lower()
                    if adv_domain and adv_domain not in seen_domains:
                        seen_domains.add(adv_domain)
                        competitors.append({
                            "domain": adv_domain,
                            "name": adv.get("name") or adv.get("advertiser_name"),
                            "advertiser_id": adv.get("advertiser_id") or adv.get("id"),
                            "region": adv.get("region"),
                        })

                await asyncio.sleep(1)

        except Exception as e:
            self.logger.debug(f"  Competitor discovery failed: {e}")

        return competitors
