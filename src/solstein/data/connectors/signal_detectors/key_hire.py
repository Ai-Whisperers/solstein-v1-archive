"""Key hire signal detector.

EPIC-022: Extracted from NewsSignalDetector for modularity.
"""

from datetime import datetime
from typing import Any

from .base import Signal, SignalDetector


class KeyHireSignalDetector(SignalDetector):
    """Detect key executive hire announcements in news articles."""

    @property
    def signal_type(self) -> str:
        return "key_hire"

    @property
    def confidence(self) -> float:
        return 0.70

    @property
    def patterns(self) -> list[str]:
        return [
            r"appoints\s+(?:new\s+)?(?:ceo|cto|cfo|coo|chief)",
            r"joins\s+as\s+(?:ceo|cto|cfo|coo|chief)",
            r"new\s+(?:ceo|cto|cfo|coo|chief)",
            r"hires\s+(?:new\s+)?(?:ceo|cto|cfo|coo|chief)",
            r"executive\s+(?:appointment|hire|joins)",
            r"appoints\s+new\s+executive",
        ]

    def detect(self, article: dict[str, Any], company_name: str) -> list[Signal]:
        """Detect key hire signals in article.

        Args:
            article: News article with title, description, content
            company_name: Company to match

        Returns:
            List of key hire signals
        """
        signals = []

        # Combine article text
        text = f"{article.get('title', '')} {article.get('description', '')}"
        content = article.get("content", "")
        if content:
            text += f" {content}"

        # Check if company mentioned
        if company_name.lower() not in text.lower():
            return signals

        # Check for key hire patterns
        if self._match_patterns(text):
            context = self._extract_context(text, company_name)

            signal = Signal(
                signal_type=self.signal_type,
                company_name=company_name,
                description=f"Key hire signal detected: {context[:100]}...",
                confidence=self.confidence,
                source=article.get("source", {}).get("name", "NewsAPI"),
                detected_at=datetime.now(),
                raw_data={
                    "article_title": article.get("title"),
                    "article_url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "context": context,
                },
            )
            signals.append(signal)

        return signals
