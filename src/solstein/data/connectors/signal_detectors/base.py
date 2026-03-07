"""Base classes for signal detection strategies.

EPIC-022: Extracted from NewsSignalDetector for modularity.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Signal:
    """Detected market signal."""

    signal_type: str
    company_name: str
    description: str
    confidence: float
    source: str
    detected_at: datetime
    raw_data: dict[str, Any]


class SignalDetector(ABC):
    """Base class for signal detection strategies.

    Each signal type (funding, partnership, key hire) implements
    its own detector with specific patterns and logic.
    """

    @property
    @abstractmethod
    def signal_type(self) -> str:
        """Return the type of signal this detector finds."""
        pass

    @property
    @abstractmethod
    def confidence(self) -> float:
        """Return the confidence score for this signal type."""
        pass

    @property
    @abstractmethod
    def patterns(self) -> list[str]:
        """Return regex patterns for detecting this signal."""
        pass

    @abstractmethod
    def detect(self, article: dict[str, Any], company_name: str) -> list[Signal]:
        """Detect signals in an article.

        Args:
            article: News article dictionary
            company_name: Company name to match

        Returns:
            List of detected signals
        """
        pass

    def _match_patterns(self, text: str) -> bool:
        """Check if text matches any detection patterns."""
        import re

        if not text:
            return False

        text_lower = text.lower()
        for pattern in self.patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def _extract_context(self, text: str, company_name: str, window: int = 150) -> str:
        """Extract context around company mention."""
        import re

        if not text:
            return ""

        # Find company name in text
        match = re.search(rf"\b{re.escape(company_name)}\b", text, re.IGNORECASE)
        if not match:
            return text[:200] if len(text) > 200 else text

        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        return text[start:end]
