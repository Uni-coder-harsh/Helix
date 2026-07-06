import re


class SafetyGuard:
    """
    Validation guard checking text against platform safety specifications.
    Audits for PII leaks (emails, phone numbers, government IDs) and toxic
    language or administrative bypass/jailbreak patterns.
    """

    def __init__(self) -> None:
        # Define PII patterns
        self.email_pattern = re.compile(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        )
        self.phone_pattern = re.compile(
            r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"
        )
        self.gov_id_pattern = re.compile(
            r"\b\d{4}[- ]?\d{4}[- ]?\d{4}\b"
        )  # Simulated general Gov ID (e.g. Aadhaar)

        # Define toxic / prompt-injection keywords
        self.bypass_keywords = [
            "ignore previous instructions",
            "system override",
            "sudo",
            "jailbreak",
            "become developer mode",
            "bypass safety",
        ]

        self.toxic_keywords = [
            "corrupt officials",
            "scam government",
            "fake scheme",
            "bribe",
        ]

    async def check_text(self, text: str) -> tuple[bool, list[str]]:
        """
        Inspect text for safety compliance.
        Returns (is_safe, list_of_violation_categories).
        """
        flagged_categories = []

        # PII checks
        if self.email_pattern.search(text):
            flagged_categories.append("PII_EMAIL_LEAK")
        if self.phone_pattern.search(text):
            flagged_categories.append("PII_PHONE_LEAK")
        if self.gov_id_pattern.search(text):
            flagged_categories.append("PII_GOV_ID_LEAK")

        # Bypass & Injection checks
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in self.bypass_keywords):
            flagged_categories.append("PROMPT_INJECTION_BYPASS")

        # Toxicity checks
        if any(keyword in text_lower for keyword in self.toxic_keywords):
            flagged_categories.append("TOXIC_CONTENT")

        is_safe = len(flagged_categories) == 0
        return is_safe, flagged_categories
