"""Shared utilities: logging, rate limiting, deduplication."""

import asyncio
import time
import sys


class Logger:
    """Simple colored logger."""
    
    COLORS = {
        "reset": "\033[0m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "dim": "\033[2m",
        "bold": "\033[1m",
        "magenta": "\033[95m",
    }

    def __init__(self, verbose=False):
        self.verbose = verbose

    def _c(self, color, text):
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def header(self, msg):
        print(f"\n{self._c('bold', self._c('cyan', f'══════ {msg} ══════'))}")

    def step(self, msg):
        print(f"  {self._c('magenta', '►')} {self._c('bold', msg)}")

    def info(self, msg):
        print(f"  {self._c('dim', msg)}")

    def success(self, msg):
        print(f"  {self._c('green', '✓')} {msg}")

    def warn(self, msg):
        print(f"  {self._c('yellow', '⚠')} {msg}")

    def error(self, msg):
        print(f"  {self._c('red', '✗')} {msg}")

    def debug(self, msg):
        if self.verbose:
            print(f"  {self._c('dim', f'  [debug] {msg}')}")


class RateLimiter:
    """Simple async rate limiter."""
    
    def __init__(self, delay=2.0):
        self.delay = delay
        self.last_request = 0

    async def wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)
        self.last_request = time.time()


def deduplicate_contacts(contacts):
    """Deduplicate contacts by email or name+domain."""
    seen = set()
    unique = []
    for c in contacts:
        # Key by email if present, else by name+domain
        key = c.get("email", "").lower() if c.get("email") else f"{c.get('name', '').lower()}|{c.get('domain', '')}"
        if key and key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def clean_email(email):
    """Clean and validate an email address."""
    if not email:
        return None
    email = email.strip().lower()
    # Remove common artifacts
    for char in ["<", ">", "(", ")", "[", "]", "'", '"', ",", ";", " "]:
        email = email.replace(char, "")
    # Basic validation
    if "@" not in email or "." not in email.split("@")[-1]:
        return None
    # Filter out obviously fake/generic emails
    skip_patterns = ["example.com", "test.com", "noreply", "no-reply", "donotreply",
                     "mailer-daemon", "postmaster@", "abuse@", "hostmaster@",
                     ".png", ".jpg", ".gif", ".css", ".js"]
    for pattern in skip_patterns:
        if pattern in email:
            return None
    if len(email) > 254 or len(email) < 5:
        return None
    return email


def clean_name(name):
    """Clean a person's name."""
    if not name:
        return None
    name = name.strip()
    # Remove common artifacts
    for char in ["\n", "\r", "\t"]:
        name = name.replace(char, " ")
    # Collapse multiple spaces
    name = " ".join(name.split())
    # Skip if it looks like junk
    if len(name) < 3 or len(name) > 100:
        return None
    if any(c in name for c in ["@", "http", "www.", "<", ">", "{"]):
        return None
    return name
