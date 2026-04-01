"""DD checklist with AI-specific additions (STORY-147).

Provides a standard PE due diligence checklist enhanced with
AI-readiness items that Solstein can auto-assess.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import ChecklistItem, ChecklistStatus

if TYPE_CHECKING:
    from solstein.domain.models import Company


def build_checklist(company: Company) -> list[ChecklistItem]:
    """Build a full DD checklist, auto-assessing items where data exists."""
    items: list[ChecklistItem] = []
    items.extend(_standard_items())
    items.extend(_ai_specific_items())
    _auto_assess(items, company)
    return items


# ---------------------------------------------------------------------------
# Standard DD items
# ---------------------------------------------------------------------------

def _standard_items() -> list[ChecklistItem]:
    """Standard PE due diligence checklist items."""
    return [
        ChecklistItem("standard", "Financial", "Verify revenue figures and growth trajectory"),
        ChecklistItem("standard", "Financial", "Review profit margins and EBITDA"),
        ChecklistItem("standard", "Financial", "Assess funding history and burn rate"),
        ChecklistItem("standard", "Financial", "Validate valuation assumptions"),
        ChecklistItem("standard", "Market", "Confirm market position and competitive landscape"),
        ChecklistItem("standard", "Market", "Review customer concentration risk"),
        ChecklistItem("standard", "Market", "Assess total addressable market"),
        ChecklistItem("standard", "Team", "Evaluate management team capability"),
        ChecklistItem("standard", "Team", "Review employee retention and satisfaction"),
        ChecklistItem("standard", "Team", "Assess key-person dependency risk"),
        ChecklistItem("standard", "Legal", "Review IP ownership and patents"),
        ChecklistItem("standard", "Legal", "Check regulatory compliance status"),
        ChecklistItem("standard", "Legal", "Review pending litigation"),
        ChecklistItem("standard", "Technology", "Assess technology architecture scalability"),
        ChecklistItem("standard", "Technology", "Review security posture and practices"),
    ]


def _ai_specific_items() -> list[ChecklistItem]:
    """AI-readiness-specific DD checklist items."""
    return [
        ChecklistItem("ai_specific", "AI Readiness", "Evaluate current AI/ML capabilities"),
        ChecklistItem("ai_specific", "AI Readiness", "Assess AI maturity level and trajectory"),
        ChecklistItem("ai_specific", "AI Readiness", "Review AI production deployments"),
        ChecklistItem("ai_specific", "Data", "Assess data infrastructure maturity"),
        ChecklistItem("ai_specific", "Data", "Review data governance and quality"),
        ChecklistItem("ai_specific", "Data", "Evaluate SaaS/cloud data platform readiness"),
        ChecklistItem("ai_specific", "Technology", "Identify legacy technology blockers for AI"),
        ChecklistItem("ai_specific", "Technology", "Review API strategy and integration capability"),
        ChecklistItem("ai_specific", "Technology", "Assess cloud-readiness of tech stack"),
        ChecklistItem("ai_specific", "Talent", "Evaluate AI/ML talent bench depth"),
        ChecklistItem("ai_specific", "Talent", "Review AI hiring pipeline and open positions"),
        ChecklistItem("ai_specific", "Transformation", "Estimate AI transformation timeline and cost"),
        ChecklistItem("ai_specific", "Transformation", "Assess transformation risk factors"),
        ChecklistItem("ai_specific", "Transformation", "Compare AI readiness to peer group"),
    ]


def _auto_assess(items: list[ChecklistItem], company: Company) -> None:
    """Auto-assess checklist items where Solstein has data."""
    for item in items:
        assessed, notes = _try_assess(item, company)
        if assessed:
            item.status = ChecklistStatus.COMPLETE
            item.notes = notes
            item.auto_assessed = True


def _try_assess(item: ChecklistItem, company: Company) -> tuple[bool, str]:
    """Attempt to auto-assess a single checklist item. Returns (assessed, notes)."""
    text = item.item.lower()

    if "revenue" in text and "growth" in text:
        if company.revenue is not None and company.growth_rate is not None:
            return True, f"Revenue: EUR {company.revenue:,.0f}, Growth: {company.growth_rate}%"

    if "ai maturity" in text:
        ai_maturity = getattr(company, "ai_maturity", None)
        if ai_maturity is not None:
            return True, f"AI maturity: {ai_maturity}"

    if "ai production" in text or "ai/ml capabilities" in text:
        ai_prod = getattr(company, "ai_in_production", None)
        ai_score = getattr(company, "ai_score", None)
        if ai_prod is not None or ai_score is not None:
            parts = []
            if ai_score is not None:
                parts.append(f"AI score: {ai_score}/10")
            if ai_prod is not None:
                parts.append(f"AI in production: {ai_prod}")
            return True, "; ".join(parts)

    if "saas" in text or "data infrastructure" in text:
        saas = getattr(company, "saas_maturity", None)
        if saas is not None and saas > 1:
            return True, f"SaaS maturity: {saas}/10"

    if "legacy technology" in text:
        stack = [s.lower() for s in getattr(company, "tech_stack", [])]
        legacy_kw = {"cobol", "mainframe", "on-premise", "on-prem", "legacy"}
        legacy = [s for s in stack if s in legacy_kw]
        if stack:
            if legacy:
                return True, f"Legacy detected: {', '.join(legacy)}"
            return True, "No legacy technology detected in stack"

    if "funding" in text or "burn rate" in text:
        funding = getattr(company, "funding_raised", None) or getattr(company, "funding", None)
        if funding is not None:
            return True, f"Total funding: EUR {funding:,.0f}"

    if "open positions" in text:
        positions = getattr(company, "open_positions", None)
        if positions is not None:
            return True, f"Open positions: {positions}"

    return False, ""
