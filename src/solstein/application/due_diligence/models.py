"""Data models for the PE Due Diligence module (STORY-147).

All DD-specific value objects live here — kept separate from the domain
model to avoid coupling the analytical overlay to the core Company entity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Red flags
# ---------------------------------------------------------------------------


class RedFlagSeverity(str, Enum):
    """How urgent a red flag is for the investment committee."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class RedFlag:
    """A single risk signal detected during due diligence."""

    category: str  # e.g. "technology", "data", "talent", "financial"
    title: str
    description: str
    severity: RedFlagSeverity
    recommendation: str
    evidence: str = ""  # what data point triggered it


# ---------------------------------------------------------------------------
# Competitive positioning
# ---------------------------------------------------------------------------


@dataclass
class CompetitivePosition:
    """How a target company stacks up against its peer group on AI readiness."""

    target_name: str
    peer_count: int
    target_ai_score: float | None
    peer_avg_ai_score: float | None
    target_rank: int  # 1 = best among peers
    percentile: float  # 0-100, higher = better
    positioning: str  # "leader", "above_average", "average", "below_average", "laggard"
    peer_scores: list[tuple[str, float | None]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# DD Checklist
# ---------------------------------------------------------------------------


class ChecklistStatus(str, Enum):
    """Progress state of a checklist item."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    NOT_APPLICABLE = "n/a"


@dataclass
class ChecklistItem:
    """A single due diligence checklist item."""

    category: str  # "standard" or "ai_specific"
    section: str  # e.g. "Technology", "Data", "Financial"
    item: str
    status: ChecklistStatus = ChecklistStatus.NOT_STARTED
    notes: str = ""
    auto_assessed: bool = False  # True if Solstein could auto-evaluate this


# ---------------------------------------------------------------------------
# Investment memo
# ---------------------------------------------------------------------------


@dataclass
class InvestmentMemo:
    """Structured investment memo with AI-readiness section.

    Fields map to a standard PE investment committee memo template
    with an added AI assessment section powered by Solstein data.
    """

    target_name: str
    prepared_date: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    # Executive summary
    executive_summary: str = ""

    # AI readiness section
    ai_readiness_summary: str = ""
    ai_readiness_score: float | None = None
    ai_readiness_tier: str | None = None
    transformation_timeline_months: float | None = None
    transformation_cost_eur: float | None = None
    transformation_risk: str | None = None

    # Risk section
    red_flag_count: int = 0
    critical_flags: list[str] = field(default_factory=list)

    # Competitive position
    competitive_summary: str = ""

    # Recommendation
    recommendation: str = ""


# ---------------------------------------------------------------------------
# Full DD report
# ---------------------------------------------------------------------------


@dataclass
class DDReport:
    """Complete due diligence report assembled by the engine."""

    target_name: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Components
    red_flags: list[RedFlag] = field(default_factory=list)
    competitive_position: CompetitivePosition | None = None
    checklist: list[ChecklistItem] = field(default_factory=list)
    investment_memo: InvestmentMemo | None = None

    # Metadata
    data_sources_used: list[str] = field(default_factory=list)
    assessment_quality: str = "standard"  # "limited", "standard", "comprehensive"
    metadata: dict[str, Any] = field(default_factory=dict)
