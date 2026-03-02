"""Base report generator with common formatting utilities (EPIC-008).

Extracted from the monolithic generator.py to enable better testability
and maintainability. This module contains shared formatting helpers and
the base ReportGenerator class.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from solstein.domain.models import Company


class ReportFormatter:
    """Shared formatting utilities for markdown reports."""

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Create filesystem-safe filename from company name."""
        return "".join(c if c.isalnum() or c in "-_ " else "_" for c in name).strip()

    @staticmethod
    def format_percentage(value: float | None) -> str:
        """Format a percentage value."""
        if value is None:
            return "N/A"
        return f"{value:.1f}%"

    @staticmethod
    def format_currency(value: float | None, currency: str = "€") -> str:
        """Format a currency value in millions."""
        if value is None:
            return "N/A"
        return f"{currency}{value:.1f}M"

    @staticmethod
    def format_large_number(value: int | None) -> str:
        """Format a large number with commas."""
        if value is None:
            return "N/A"
        return f"{value:,}"
    @staticmethod
    def format_score(value: float | None) -> str:
        """Format a score value to 2 decimal places."""
        if value is None:
            return "N/A"
        return f"{value:.2f}"


    @staticmethod
    def get_tier_emoji(tier: str | None) -> str:
        """Get emoji for company tier."""
        tier_emojis = {
            "Phoenix": "🔥",
            "Salt": "🧂",
            "Lead": "⚓",
        }
        return tier_emojis.get(tier or "", "❓")

    @staticmethod
    def get_threat_emoji(threat: str | None) -> str:
        """Get emoji for threat level."""
        threat_emojis = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🟢",
            "None": "⚪",
        }
        return threat_emojis.get(threat or "", "❓")

    @staticmethod
    def avg(values: list[float]) -> float:
        """Calculate average of values."""
        return sum(values) / len(values) if values else 0.0

    @staticmethod
    def median(values: list[float]) -> float:
        """Calculate median of values."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
        return sorted_vals[mid]


class ScoreInterpreter:
    """Interpret score values into human-readable assessments."""

    @staticmethod
    def interpret_growth(score: float | None) -> str:
        """Interpret growth score."""
        if score is None:
            return "Unknown"
        if score >= 8:
            return "Exceptional growth trajectory"
        elif score >= 6:
            return "Strong growth"
        elif score >= 4:
            return "Moderate growth"
        elif score >= 2:
            return "Slow growth"
        return "Declining or stagnant"

    @staticmethod
    def interpret_health(score: float | None) -> str:
        """Interpret financial health score."""
        if score is None:
            return "Unknown"
        if score >= 8:
            return "Excellent financial health"
        elif score >= 6:
            return "Strong financial position"
        elif score >= 4:
            return "Adequate financial health"
        elif score >= 2:
            return "Financial stress detected"
        return "Critical financial condition"

    @staticmethod
    def interpret_position(score: float | None) -> str:
        """Interpret competitive position score."""
        if score is None:
            return "Unknown"
        if score >= 8:
            return "Market leader"
        elif score >= 6:
            return "Strong competitive position"
        elif score >= 4:
            return "Average competitive position"
        elif score >= 2:
            return "Weak competitive position"
        return "Vulnerable market position"


class BaseReportGenerator:
    """Base class for report generators with common utilities."""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path("data/output/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.formatter = ReportFormatter()
        self.interpreter = ScoreInterpreter()

    def _write_report(self, content: str, output_path: Path) -> Path:
        """Write report content to file."""
        output_path.write_text(content, encoding="utf-8")
        logger.debug(f"Report written: {output_path}")
        return output_path
