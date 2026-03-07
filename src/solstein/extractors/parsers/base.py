"""Base parser for markdown content extraction.

EPIC-022: Extracted from MarkdownExtractor for modularity.
"""

import re
from abc import ABC, abstractmethod
from typing import Any


class ContentParser(ABC):
    """Base class for content parsing strategies.

    Each parser handles a specific aspect of markdown content extraction.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this parser."""
        pass

    @abstractmethod
    def parse(self, content: str) -> dict[str, Any]:
        """Parse content and extract data.

        Args:
            content: Markdown content to parse

        Returns:
            Dictionary of extracted data
        """
        pass


class PatternBasedParser(ContentParser):
    """Parser that uses regex patterns for extraction."""

    def __init__(self, patterns: dict[str, str]) -> None:
        """Initialize with patterns.

        Args:
            patterns: Dictionary of field names to regex patterns
        """
        self._patterns = {key: re.compile(pattern) for key, pattern in patterns.items()}

    @property
    def name(self) -> str:
        return "pattern_based"

    def parse(self, content: str) -> dict[str, Any]:
        """Parse content using regex patterns."""
        data: dict[str, Any] = {}

        for key, pattern in self._patterns.items():
            match = pattern.search(content)
            if match:
                data[key] = match.group(1).strip()

        return data

    def add_pattern(self, name: str, pattern: str) -> None:
        """Add a new pattern."""
        self._patterns[name] = re.compile(pattern)
