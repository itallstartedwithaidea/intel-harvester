"""DNS & WHOIS reconnaissance module.
Pulls MX records, nameservers, TXT/SPF records, WHOIS registrant info,
and certificate transparency logs for email discovery.
"""

import asyncio
import json
import re
import subprocess

from modules.utils import clean_email


class DNSRecon:
    def __init__(self, domain, config, logger):
        self.domain = domain
        self.config = config
        self.logger = logger
        self.emails = set()
        self.meta = {
            "mx_provider": None,
            "nameservers": [],
            "registrant": None,
        }

    async def run(self):
        """Run all DNS recon methods."""
        await self._mx_records()
        await self._nameservers()
        await self._txt_records()
        await self._whois()
        await self._crtsh()

        return {
            "emails": list(self.emails),
            "meta": self.meta,
        }

    async def _mx_records(self):
        """Get MX records to determine email provider."""
        try:
            result = await self._run_cmd(f"dig +short MX {self.domain}")
            if result:
                lines = result.strip().split("\n")
                mx_hosts = [line.split()[-1].rstrip(".") for line in lines if line.strip()]
                
                # Detect provider
                mx_text = " ".join(mx_hosts).lower()
                if "google" in mx_text or "gmail" in mx_text:
                    self.meta["mx_provider"] = "Google Workspace"
                elif "outlook" in mx_text or "microsoft" in mx_text:
                    self.meta["mx_provider"] = "Microsoft 365"
                elif "zoho" in mx_text:
                    self.meta["mx_provider"] = "Zoho"
                elif "titan" in mx_text:
                    self.meta["mx_provider"] = "Titan"
                elif "proton" in mx_text:
                    self.meta["mx_provider"] = "ProtonMail"
                elif "mimecast" in mx_text:
                    self.meta["mx_provider"] = "Mimecast"
                elif "barracuda" in mx_text:
                    self.meta["mx_provider"] = "Barracuda"
                else:
                    self.meta["mx_provider"] = mx_hosts[0] if mx_hosts else "unknown"
                    
                self.logger.debug(f"MX: {', '.join(mx_hosts)}")
        except Exception as e:
            self.logger.debug(f"MX lookup failed: {e}")

    async def _nameservers(self):
        """Get nameservers — often reveals hosting provider."""
        try:
            result = await self._run_cmd(f"dig +short NS {self.domain}")
            if result:
                ns_list = [ns.strip().rstrip(".") for ns in result.strip().split("\n") if ns.strip()]
                self.meta["nameservers"] = ns_list
                self.logger.debug(f"NS: {', '.join(ns_list)}")
        except Exception as e:
            self.logger.debug(f"NS lookup failed: {e}")

    async def _txt_records(self):
        """Parse TXT/SPF records for emails and connected services."""
        try:
            result = await self._run_cmd(f"dig +short TXT {self.domain}")
            if result:
                # Extract emails from SPF, DKIM, DMARC records
                emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', result)
                for email in emails:
                    cleaned = clean_email(email)
                    if cleaned and self.domain in cleaned:
                        self.emails.add(cleaned)
                
                # Look for interesting services in TXT records
                services = []
                if "google-site-verification" in result:
                    services.append("Google Search Console")
                if "v=spf1" in result:
                    services.append("SPF")
                if "facebook" in result.lower():
                    services.append("Facebook")
                if "hubspot" in result.lower():
                    services.append("HubSpot")
                if "salesforce" in result.lower():
                    services.append("Salesforce")
                if "zendesk" in result.lower():
                    services.append("Zendesk")
                    
                if services:
                    self.logger.debug(f"TXT services: {', '.join(services)}")
        except Exception as e:
            self.logger.debug(f"TXT lookup failed: {e}")

    async def _whois(self):
        """Extract registrant info from WHOIS."""
        try:
            result = await self._run_cmd(f"whois {self.domain}")
            if result:
                # Extract registrant email
                for pattern in [
                    r'Registrant Email:\s*(.+)',
                    r'Admin Email:\s*(.+)',
                    r'Tech Email:\s*(.+)',
                    r'OrgAbuseEmail:\s*(.+)',
                    r'OrgTechEmail:\s*(.+)',
                ]:
                    matches = re.findall(pattern, result, re.IGNORECASE)
                    for email in matches:
                        cleaned = clean_email(email.strip())
                        if cleaned:
                            self.emails.add(cleaned)

                # Extract registrant name/org
                for pattern in [
                    r'Registrant Organization:\s*(.+)',
                    r'Registrant Name:\s*(.+)',
                    r'OrgName:\s*(.+)',
                ]:
                    match = re.search(pattern, result, re.IGNORECASE)
                    if match:
                        val = match.group(1).strip()
                        if val and "REDACTED" not in val.upper() and "DATA PROTECTED" not in val.upper():
                            self.meta["registrant"] = val
                            break
        except Exception as e:
            self.logger.debug(f"WHOIS lookup failed: {e}")

    async def _crtsh(self):
        """Query Certificate Transparency logs via crt.sh for subdomains and emails."""
        try:
            import requests
            url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
            resp = requests.get(url, timeout=self.config["timeout"])
            if resp.status_code == 200:
                data = resp.json()
                # Extract unique common names — these reveal subdomains
                names = set()
                for entry in data:
                    cn = entry.get("common_name", "")
                    if cn and self.domain in cn:
                        names.add(cn)
                    name_val = entry.get("name_value", "")
                    for name in name_val.split("\n"):
                        name = name.strip()
                        if name and self.domain in name:
                            names.add(name)
                
                # Look for email-related subdomains
                for name in names:
                    if any(kw in name.lower() for kw in ["mail", "smtp", "webmail", "autodiscover"]):
                        self.logger.debug(f"  crt.sh mail subdomain: {name}")
                
                self.logger.debug(f"  crt.sh found {len(names)} unique names")
        except Exception as e:
            self.logger.debug(f"crt.sh lookup failed: {e}")

    async def _run_cmd(self, cmd):
        """Run a shell command and return output."""
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)
            return stdout.decode("utf-8", errors="replace")
        except (asyncio.TimeoutError, Exception):
            return ""
