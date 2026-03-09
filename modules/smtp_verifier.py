"""SMTP email verification module.
Checks if an email mailbox exists by connecting to the MX server
and issuing RCPT TO without actually sending a message.

Note: Many mail servers block or lie about RCPT TO results.
This is best-effort verification, not guaranteed.
"""

import asyncio
import socket
import smtplib
import re

from modules.utils import Logger


class SMTPVerifier:
    def __init__(self, domain, emails, config, logger):
        self.domain = domain
        self.emails = emails
        self.config = config
        self.logger = logger
        self.mx_host = None

    async def run(self):
        """Verify a list of emails via SMTP RCPT TO."""
        results = {}

        if not self.emails:
            return results

        # Get MX host
        self.mx_host = await self._get_mx_host()
        if not self.mx_host:
            self.logger.debug("  Could not resolve MX host — skipping SMTP verification")
            return {email: None for email in self.emails}

        self.logger.debug(f"  MX host: {self.mx_host}")

        # Verify each email
        for email in self.emails:
            try:
                result = await self._verify_email(email)
                results[email] = result
                self.logger.debug(f"  {email}: {'✓' if result else '✗' if result is False else '?'}")
                await asyncio.sleep(0.5)  # Be polite to the mail server
            except Exception as e:
                results[email] = None
                self.logger.debug(f"  {email}: error ({e})")

        return results

    async def _get_mx_host(self):
        """Resolve the MX host for the domain."""
        try:
            proc = await asyncio.create_subprocess_shell(
                f"dig +short MX {self.domain} | sort -n | head -1",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            result = stdout.decode().strip()
            if result:
                # MX record format: "10 mail.example.com."
                parts = result.split()
                if len(parts) >= 2:
                    return parts[-1].rstrip(".")
                return parts[0].rstrip(".")
        except Exception:
            pass
        return None

    async def _verify_email(self, email):
        """Verify a single email via SMTP RCPT TO.
        
        Returns:
            True  — mailbox exists (250 response)
            False — mailbox rejected (550/551/552/553 response)
            None  — inconclusive (server blocked, catch-all, timeout)
        """
        if not self.mx_host:
            return None

        try:
            # Run the SMTP check in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, self._smtp_check, email),
                timeout=15
            )
            return result
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None

    def _smtp_check(self, email):
        """Synchronous SMTP RCPT TO check."""
        try:
            smtp = smtplib.SMTP(timeout=10)
            smtp.connect(self.mx_host, 25)
            smtp.ehlo_or_helo_if_needed()

            # Use a plausible sender domain
            from_addr = f"verify@{self.domain}"
            
            code_from, _ = smtp.mail(from_addr)
            if code_from != 250:
                smtp.quit()
                return None  # Server rejected our MAIL FROM — can't verify

            code_rcpt, msg = smtp.rcpt(email)
            smtp.quit()

            if code_rcpt == 250:
                return True
            elif code_rcpt in (550, 551, 552, 553):
                return False
            else:
                return None  # Ambiguous response

        except smtplib.SMTPServerDisconnected:
            return None
        except smtplib.SMTPConnectError:
            return None
        except socket.timeout:
            return None
        except socket.gaierror:
            return None
        except ConnectionRefusedError:
            return None
        except Exception:
            return None


class CatchAllDetector:
    """Detect if a domain has a catch-all email configuration.
    If it does, SMTP verification is useless — all addresses return 250.
    """
    
    @staticmethod
    async def is_catch_all(domain, mx_host):
        """Test with a random email that definitely doesn't exist."""
        import random
        import string
        random_local = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        fake_email = f"{random_local}@{domain}"
        
        verifier = SMTPVerifier(domain, [fake_email], {"timeout": 10}, Logger(verbose=False))
        verifier.mx_host = mx_host
        results = await verifier.run()
        
        # If the random email "exists", it's a catch-all
        return results.get(fake_email) is True
