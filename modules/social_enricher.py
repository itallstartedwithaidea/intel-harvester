"""Social media enrichment module.
Searches for people on LinkedIn, Twitter/X, and other platforms
to find profile URLs and additional context.
"""

import asyncio
import re
import requests
from urllib.parse import quote

from modules.utils import clean_name


class SocialEnricher:
    def __init__(self, domain, people, config, logger):
        self.domain = domain
        self.people = people
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config["user_agent"],
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })

    async def run(self):
        """Enrich people with social media profiles."""
        results = {}

        for person in self.people:
            name = person.get("name", "")
            if not name or len(name.split()) < 2:
                continue

            profile = {}
            
            # Search for LinkedIn profile
            linkedin_url = await self._find_linkedin(name)
            if linkedin_url:
                profile["linkedin"] = linkedin_url

            # Search for Twitter/X profile
            twitter_url = await self._find_twitter(name)
            if twitter_url:
                profile["twitter"] = twitter_url

            if profile:
                results[name] = profile
                self.logger.debug(f"  Enriched: {name} -> {profile}")

            await asyncio.sleep(self.config["delay"])

        return results

    async def _find_linkedin(self, name):
        """Search for a person's LinkedIn profile via DuckDuckGo."""
        try:
            query = f'site:linkedin.com/in "{name}" "{self.domain}"'
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            resp = self.session.get(url, timeout=self.config["timeout"])
            
            if resp.status_code == 200:
                # Look for LinkedIn profile URLs in results
                matches = re.findall(r'https?://(?:www\.)?linkedin\.com/in/[\w-]+', resp.text)
                if matches:
                    return matches[0]
                
                # Also check for LinkedIn URLs in DuckDuckGo redirect links
                matches2 = re.findall(r'linkedin\.com/in/([\w-]+)', resp.text)
                if matches2:
                    return f"https://www.linkedin.com/in/{matches2[0]}"
        except Exception as e:
            self.logger.debug(f"  LinkedIn search failed for {name}: {e}")
        
        return None

    async def _find_twitter(self, name):
        """Search for a person's Twitter/X profile via DuckDuckGo."""
        try:
            query = f'site:twitter.com OR site:x.com "{name}" "{self.domain}"'
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            resp = self.session.get(url, timeout=self.config["timeout"])
            
            if resp.status_code == 200:
                # Look for Twitter/X profile URLs
                patterns = [
                    r'https?://(?:www\.)?twitter\.com/([\w]+)',
                    r'https?://(?:www\.)?x\.com/([\w]+)',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, resp.text)
                    for match in matches:
                        # Filter out Twitter's own pages
                        if match.lower() not in ["search", "home", "explore", "notifications",
                                                   "messages", "settings", "i", "hashtag",
                                                   "intent", "share", "login", "signup"]:
                            return f"https://x.com/{match}"
        except Exception as e:
            self.logger.debug(f"  Twitter search failed for {name}: {e}")
        
        return None


class CompanySocialFinder:
    """Find company social media profiles from the website."""
    
    @staticmethod
    def find_company_socials(html):
        """Extract company social media links from HTML."""
        socials = {}
        
        patterns = {
            "linkedin": r'https?://(?:www\.)?linkedin\.com/company/[\w-]+',
            "twitter": r'https?://(?:www\.)?(?:twitter|x)\.com/[\w]+',
            "facebook": r'https?://(?:www\.)?facebook\.com/[\w.]+',
            "instagram": r'https?://(?:www\.)?instagram\.com/[\w.]+',
            "youtube": r'https?://(?:www\.)?youtube\.com/(?:c/|channel/|@)[\w-]+',
            "github": r'https?://(?:www\.)?github\.com/[\w-]+',
        }
        
        for platform, pattern in patterns.items():
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                # Dedupe and take the first
                socials[platform] = list(dict.fromkeys(matches))[0]
        
        return socials
