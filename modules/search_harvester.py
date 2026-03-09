"""Search engine harvester module.
Scrapes Google, Bing, and DuckDuckGo for emails and people
associated with a domain. Inspired by theHarvester and EmailHarvester.
"""

import asyncio
import re
import time

import requests
from bs4 import BeautifulSoup

from modules.utils import clean_email, clean_name


class SearchHarvester:
    def __init__(self, domain, config, logger):
        self.domain = domain
        self.config = config
        self.logger = logger
        self.emails = set()
        self.people = []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config["user_agent"],
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })

    async def run(self):
        """Run search engine harvesting."""
        # DuckDuckGo — most reliable, least likely to block
        await self._duckduckgo_emails()
        await asyncio.sleep(self.config["delay"])
        
        await self._duckduckgo_people()
        await asyncio.sleep(self.config["delay"])

        # Bing — decent results, moderate blocking
        await self._bing_emails()
        await asyncio.sleep(self.config["delay"])

        # Google — best results but aggressive blocking
        # Use sparingly and with longer delays
        await self._google_emails()
        await asyncio.sleep(self.config["delay"])

        # GitHub — developer emails from commit history
        await self._github_emails()

        return {
            "emails": list(self.emails),
            "people": self.people,
        }

    async def _duckduckgo_emails(self):
        """Search DuckDuckGo for emails at domain."""
        queries = [
            f'"@{self.domain}"',
            f'site:{self.domain} email',
            f'site:{self.domain} contact',
        ]
        for query in queries:
            try:
                url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
                resp = self.session.get(url, timeout=self.config["timeout"])
                if resp.status_code == 200:
                    self._extract_emails(resp.text)
                    self.logger.debug(f"  DDG query: {query}")
                await asyncio.sleep(self.config["delay"])
            except Exception as e:
                self.logger.debug(f"  DDG failed: {e}")

    async def _duckduckgo_people(self):
        """Search DuckDuckGo for people at the company."""
        title_queries = [
            f'site:linkedin.com/in "{self.domain}" CEO OR founder OR director',
            f'"{self.domain}" "team" OR "leadership" OR "about"',
        ]
        for query in title_queries:
            try:
                url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
                resp = self.session.get(url, timeout=self.config["timeout"])
                if resp.status_code == 200:
                    self._extract_linkedin_people(resp.text)
                await asyncio.sleep(self.config["delay"])
            except Exception as e:
                self.logger.debug(f"  DDG people failed: {e}")

    async def _bing_emails(self):
        """Search Bing for emails at domain."""
        queries = [
            f'"@{self.domain}"',
            f'site:{self.domain} email contact',
        ]
        for query in queries:
            try:
                url = f"https://www.bing.com/search?q={requests.utils.quote(query)}&count=50"
                resp = self.session.get(url, timeout=self.config["timeout"])
                if resp.status_code == 200:
                    self._extract_emails(resp.text)
                    self.logger.debug(f"  Bing query: {query}")
                await asyncio.sleep(self.config["delay"])
            except Exception as e:
                self.logger.debug(f"  Bing failed: {e}")

    async def _google_emails(self):
        """Search Google for emails at domain (careful — will block fast)."""
        try:
            query = f'"@{self.domain}"'
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num=50"
            resp = self.session.get(url, timeout=self.config["timeout"])
            if resp.status_code == 200:
                self._extract_emails(resp.text)
                self.logger.debug(f"  Google query: {query}")
            elif resp.status_code == 429:
                self.logger.debug("  Google rate limited — skipping")
        except Exception as e:
            self.logger.debug(f"  Google failed: {e}")

    async def _github_emails(self):
        """Search GitHub for emails in commit history."""
        try:
            # Search for commits by domain
            url = f"https://api.github.com/search/commits?q={self.domain}&per_page=30"
            headers = {
                "Accept": "application/vnd.github.cloak-preview+json",
                "User-Agent": self.config["user_agent"],
            }
            resp = self.session.get(url, headers=headers, timeout=self.config["timeout"])
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", []):
                    commit = item.get("commit", {})
                    author = commit.get("author", {})
                    email = clean_email(author.get("email", ""))
                    name = clean_name(author.get("name", ""))
                    if email and self.domain in email:
                        self.emails.add(email)
                        if name:
                            self.people.append({
                                "name": name,
                                "title": "Developer (GitHub)",
                                "source": "github",
                                "email": email,
                            })
                self.logger.debug(f"  GitHub found {len(data.get('items', []))} commits")
            
            # Also search for users associated with domain
            url2 = f"https://api.github.com/search/users?q={self.domain}+in:email&per_page=10"
            resp2 = self.session.get(url2, timeout=self.config["timeout"])
            if resp2.status_code == 200:
                data2 = resp2.json()
                for user in data2.get("items", []):
                    login = user.get("login", "")
                    if login:
                        # Fetch user details for email
                        user_url = f"https://api.github.com/users/{login}"
                        user_resp = self.session.get(user_url, timeout=self.config["timeout"])
                        if user_resp.status_code == 200:
                            user_data = user_resp.json()
                            email = clean_email(user_data.get("email", ""))
                            name = clean_name(user_data.get("name", ""))
                            if email:
                                self.emails.add(email)
                                if name:
                                    self.people.append({
                                        "name": name,
                                        "title": f"Developer (@{login})",
                                        "source": "github",
                                        "email": email,
                                    })
        except Exception as e:
            self.logger.debug(f"  GitHub search failed: {e}")

    def _extract_emails(self, html):
        """Extract emails matching the domain from HTML."""
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', html)
        for email in emails:
            cleaned = clean_email(email)
            if cleaned and self.domain.lower() in cleaned.lower():
                self.emails.add(cleaned)

    def _extract_linkedin_people(self, html):
        """Extract names and titles from LinkedIn search results."""
        soup = BeautifulSoup(html, "html.parser")
        
        # DuckDuckGo result snippets often contain "Name - Title - Company | LinkedIn"
        for result in soup.find_all(["a", "span", "div"]):
            text = result.get_text(strip=True)
            
            # Pattern: "First Last - Title - Company | LinkedIn"
            if "linkedin" in text.lower() and "|" in text:
                parts = text.split("|")[0].strip()
                if " - " in parts:
                    segments = parts.split(" - ")
                    if len(segments) >= 2:
                        name = clean_name(segments[0].strip())
                        title = segments[1].strip() if len(segments) > 1 else ""
                        if name and len(name.split()) >= 2:
                            self.people.append({
                                "name": name,
                                "title": title,
                                "source": "linkedin_search",
                            })
            
            # Pattern in href: linkedin.com/in/firstname-lastname
            href = result.get("href", "")
            if "linkedin.com/in/" in href:
                slug = href.split("linkedin.com/in/")[-1].split("?")[0].split("/")[0]
                # Convert slug to name: "john-smith-123abc" -> "John Smith"
                name_parts = slug.split("-")
                # Remove trailing numbers/IDs
                name_parts = [p for p in name_parts if not p.isdigit() and len(p) > 1]
                if 2 <= len(name_parts) <= 4:
                    name = " ".join(p.capitalize() for p in name_parts)
                    name = clean_name(name)
                    if name:
                        self.people.append({
                            "name": name,
                            "title": "",
                            "source": "linkedin_search",
                            "linkedin_slug": slug,
                        })
