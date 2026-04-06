# guardrails/pii_redactor.py

import re
from typing import List, Tuple


# Regex patterns for common PII types
PII_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "PHONE": r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}


class PIIRedactor:
    """Regex-based PII redactor. Detects and masks common PII patterns."""

    def __init__(self, patterns: dict | None = None):
        self.patterns = patterns or PII_PATTERNS

    def redact(self, text: str) -> Tuple[str, List[dict]]:
        """
        Redact PII from text.
        Returns (redacted_text, list_of_detected_entities).
        Each entity dict has keys: type, value, start, end, score.
        """
        entities = []
        redacted = text

        for pii_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                entities.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "score": 0.95,
                })

        # Replace matches (process longest-first to avoid offset issues)
        for entity in sorted(entities, key=lambda e: e["start"], reverse=True):
            placeholder = f"[{entity['type']}]"
            redacted = redacted[:entity["start"]] + placeholder + redacted[entity["end"]:]

        return redacted, entities

    async def redact_async(self, text: str) -> Tuple[str, List[dict]]:
        """Async wrapper for redact (regex is CPU-bound, but keeps interface consistent)."""
        return self.redact(text)


# --- Quick test ---
if __name__ == "__main__":
    redactor = PIIRedactor()
    tests = [
        "My email is vivek@example.com and phone is 555-123-4567",
        "SSN: 123-45-6789, card: 4111 1111 1111 1111",
        "No PII in this message about my order.",
    ]
    for msg in tests:
        clean, found = redactor.redact(msg)
        print(f"Original: {msg}")
        print(f"Redacted: {clean}")
        print(f"Found:    {[e['type'] for e in found]}\n")