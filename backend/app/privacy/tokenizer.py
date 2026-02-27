import re
from typing import List


class Tokenizer:
    """Simple text tokenizer for preprocessing before PII detection."""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Split text into tokens (words and punctuation)."""
        return re.findall(r"\b\w+\b|[^\w\s]", text)

    @staticmethod
    def sentence_split(text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize whitespace and strip text."""
        return re.sub(r"\s+", " ", text).strip()
