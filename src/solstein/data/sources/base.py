"""Base utilities for data sources."""

from __future__ import annotations


def analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment analysis."""
    text_lower = text.lower()

    positive_words = [
        "growth",
        "profit",
        "revenue",
        "success",
        "win",
        "launch",
        "expand",
        "innovation",
        "leader",
        "partnership",
        "award",
        "acquisition",
        "positive",
        "strong",
        "beat",
        "bullish",
    ]
    negative_words = [
        "loss",
        "lawsuit",
        "investigation",
        "scandal",
        "fire",
        "layoff",
        "bankruptcy",
        "decline",
        "weak",
        "miss",
        "warning",
        "fraud",
        "investor",
        "concern",
        "risk",
    ]

    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)

    if pos_count > neg_count + 1:
        return "positive"
    elif neg_count > pos_count + 1:
        return "negative"
    return "neutral"
