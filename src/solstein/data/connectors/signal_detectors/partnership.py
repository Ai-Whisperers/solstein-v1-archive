"""Partnership signal detector.

EPIC-022: Extracted from NewsSignalDetector for modularity.
"""

from datetime import datetime, timezone
from typing import Any

from .base import Signal, SignalDetector


class PartnershipSignalDetector(SignalDetector):
    """Detect partnership announcements in news articles."""

    @property
    def signal_type(self) -> str:
        return "partnership"

    @property
    def confidence(self) -> float:
        return 0.72

    @property
    def patterns(self) -> list[str]:
        return [
            r"partnership",
            r"collaboration",
            r"integrates\s+with",
            r"announces\s+partnership",
            r"partners\s+with",
            r"strategic\s+alliance",
            r"joint\s+venture",
            r"announces\s+collaboration",
        ]

    def detect(self, article: dict[str, Any], company_name: str) -> list[Signal]:
        """Detect partnership signals in article.

        Args:
            article: News article with title, description, content
            company_name: Company to match

        Returns:
            List of partnership signals
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

        # Check for partnership patterns
        if self._match_patterns(text):
            context = self._extract_context(text, company_name)

            signal = Signal(
                signal_type=self.signal_type,
                company_name=company_name,
                description=f"Partnership signal detected: {context[:100]}...",
                confidence=self.confidence,
                source=article.get("source", {}).get("name", "NewsAPI"),
                detected_at=datetime.now(tz=timezone.utc),
                raw_data={
                    "article_title": article.get("title"),
                    "article_url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "context": context,
                },
            )
            signals.append(signal)

        return signals
