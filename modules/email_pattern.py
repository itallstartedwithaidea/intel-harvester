"""Email pattern detection and generation engine.
Analyzes confirmed emails to detect the naming pattern,
then generates candidate emails for people found without emails.
"""

import re
from collections import Counter
from modules.utils import clean_email


# Common email patterns at companies
PATTERNS = {
    "first.last":       lambda f, l: f"{f}.{l}",
    "firstlast":        lambda f, l: f"{f}{l}",
    "first_last":       lambda f, l: f"{f}_{l}",
    "flast":            lambda f, l: f"{f[0]}{l}",
    "firstl":           lambda f, l: f"{f}{l[0]}",
    "f.last":           lambda f, l: f"{f[0]}.{l}",
    "first":            lambda f, l: f"{f}",
    "last.first":       lambda f, l: f"{l}.{f}",
    "lastf":            lambda f, l: f"{l}{f[0]}",
    "last":             lambda f, l: f"{l}",
    "last_first":       lambda f, l: f"{l}_{f}",
    "first.l":          lambda f, l: f"{f}.{l[0]}",
    "fl":               lambda f, l: f"{f[0]}{l[0]}",
}


class EmailPatternEngine:
    def __init__(self, domain, confirmed_emails, people, logger):
        self.domain = domain
        self.confirmed_emails = [e for e in confirmed_emails if domain.lower() in e.lower()]
        self.people = people
        self.logger = logger
        self.detected_pattern = None

    def run(self):
        """Detect pattern and generate emails for unmatched people."""
        # Step 1: Detect the email pattern
        self.detected_pattern = self._detect_pattern()
        
        # Step 2: Generate emails for people without them
        generated = []
        if self.detected_pattern:
            generated = self._generate_emails()

        return {
            "pattern": self.detected_pattern,
            "generated_emails": generated,
        }

    def _detect_pattern(self):
        """Analyze confirmed emails to detect the naming pattern."""
        if not self.confirmed_emails:
            return None

        pattern_votes = Counter()

        for email in self.confirmed_emails:
            local_part = email.split("@")[0].lower()
            
            # Try to find a matching person for this email
            for person in self.people:
                name_parts = person.get("name", "").lower().split()
                if len(name_parts) < 2:
                    continue
                first = name_parts[0]
                last = name_parts[-1]

                # Test each pattern
                for pattern_name, pattern_fn in PATTERNS.items():
                    try:
                        candidate = pattern_fn(first, last).lower()
                        if candidate == local_part:
                            pattern_votes[pattern_name] += 1
                    except (IndexError, TypeError):
                        continue

        # If we have votes, use the winner
        if pattern_votes:
            winner = pattern_votes.most_common(1)[0]
            self.logger.debug(f"  Pattern votes: {dict(pattern_votes)}")
            return winner[0]

        # Fallback: analyze the structure of confirmed emails without matching to people
        return self._infer_pattern_from_structure()

    def _infer_pattern_from_structure(self):
        """Infer pattern from email structure when we can't match to known people."""
        structures = Counter()
        
        for email in self.confirmed_emails:
            local = email.split("@")[0].lower()
            
            # Skip generic emails
            if local in ["info", "contact", "hello", "support", "sales", "admin", "hr", "team"]:
                continue

            if "." in local:
                parts = local.split(".")
                if len(parts) == 2:
                    if len(parts[0]) == 1:
                        structures["f.last"] += 1
                    elif len(parts[1]) == 1:
                        structures["first.l"] += 1
                    else:
                        structures["first.last"] += 1
            elif "_" in local:
                structures["first_last"] += 1
            elif len(local) > 3:
                # Check if it looks like flast (one char + longer string)
                if len(local) >= 4 and local[1:].isalpha():
                    structures["flast"] += 1
                else:
                    structures["firstlast"] += 1

        if structures:
            return structures.most_common(1)[0][0]
        return None

    def _generate_emails(self):
        """Generate candidate emails for people who don't have one."""
        if not self.detected_pattern or self.detected_pattern not in PATTERNS:
            return []

        pattern_fn = PATTERNS[self.detected_pattern]
        generated = []
        existing_emails = set(e.lower() for e in self.confirmed_emails)

        for person in self.people:
            # Skip if person already has an email
            if person.get("email"):
                continue

            name_parts = person.get("name", "").lower().split()
            if len(name_parts) < 2:
                continue

            first = self._normalize_name(name_parts[0])
            last = self._normalize_name(name_parts[-1])

            if not first or not last:
                continue

            try:
                local_part = pattern_fn(first, last)
                candidate = f"{local_part}@{self.domain}".lower()
                
                # Don't duplicate existing emails
                if candidate not in existing_emails:
                    generated.append(candidate)
                    # Also update the person record
                    person["email"] = candidate
                    person["email_source"] = "pattern_generated"
            except (IndexError, TypeError):
                continue

        return generated

    def _normalize_name(self, name):
        """Normalize a name part for email generation."""
        # Remove accents, special chars
        name = re.sub(r'[^a-z]', '', name.lower())
        return name if len(name) >= 1 else None
