"""PE Due Diligence Integration Module (STORY-147, EPIC-038).

Provides AI-readiness-aware due diligence capabilities:

- Red flag identification from company signals
- Competitive AI positioning against peer group
- Due diligence checklist with AI-specific items
- Structured investment memo generation
- DD report assembly from Solstein intelligence

Usage::

    from solstein.application.due_diligence import DueDiligenceEngine
    engine = DueDiligenceEngine()
    report = engine.run(target=company, peers=[peer1, peer2])
"""

from .engine import DueDiligenceEngine
from .models import (
    ChecklistItem,
    ChecklistStatus,
    CompetitivePosition,
    DDReport,
    InvestmentMemo,
    RedFlag,
    RedFlagSeverity,
)

__all__ = [
    "ChecklistItem",
    "ChecklistStatus",
    "CompetitivePosition",
    "DDReport",
    "DueDiligenceEngine",
    "InvestmentMemo",
    "RedFlag",
    "RedFlagSeverity",
]
