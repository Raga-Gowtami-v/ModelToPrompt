import re
from typing import List, Dict


# Common PII regex patterns
PII_PATTERNS = {
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "PHONE": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "IP_ADDRESS": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "DATE_OF_BIRTH": r"\b(?:0[1-9]|1[0-2])[/\-](?:0[1-9]|[12]\d|3[01])[/\-](?:19|20)\d{2}\b",
    "AADHAAR": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    "PAN": r"\b[A-Z]{5}\d{4}[A-Z]\b",
}


class RegexDetector:
    def __init__(self, patterns: Dict[str, str] = None):
        self.patterns = patterns or PII_PATTERNS

    def detect(self, text: str) -> List[Dict]:
        """Scan text for PII using regex patterns.

        Returns a list of detections with type, value, start, and end positions.
        """
        detections = []
        for pii_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                detections.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.95,
                    "detector": "regex",
                })
        return detections

    def mask(self, text: str, detections: List[Dict] = None) -> str:
        """Replace detected PII with masked placeholders."""
        if detections is None:
            detections = self.detect(text)

        # Sort by start position in reverse to preserve offsets
        sorted_detections = sorted(detections, key=lambda d: d["start"], reverse=True)
        masked_text = text
        for det in sorted_detections:
            placeholder = f"[{det['type']}]"
            masked_text = masked_text[:det["start"]] + placeholder + masked_text[det["end"]:]
        return masked_text
