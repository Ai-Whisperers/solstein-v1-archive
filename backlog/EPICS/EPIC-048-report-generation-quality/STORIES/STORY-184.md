# STORY-184: Replace Boilerplate Deep Analysis with Actual Signal-Based Weaknesses

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | M (2–3 days) |
| **Epic** | EPIC-048 Report Generation Quality |
| **Created** | 2026-03-01 |
| **Risk** | Medium — requires signal extraction logic |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED QUALITY ISSUE** — verified by live execution on 2026-03-01.

```markdown
<!-- deep-analysis.md for Eneve -->
## Weaknesses
No critical weaknesses identified.

## Opportunities
No specific opportunities identified at this time.
```

This is hardcoded boilerplate. Eneve has actual weaknesses that should be identified:
- **Tier 4** (lowest tier) — structural weakness
- **Only €2M funding** — undercapitalized vs peers
- **150 employees** — small team, limited execution capacity
- **Revenue €5M** — small scale, limited market presence

The deep analysis report should derive weaknesses from actual company attributes, not print generic text.

---

## Problem Statement

The `deep-analysis.md` report is a critical deliverable for PE/VC analysts. It should provide actionable intelligence about a company's competitive position, risks, and opportunities. Currently it prints:
- "No critical weaknesses identified" — always
- "No specific opportunities identified" — always
- Generic SWOT categories without actual content

This makes the report worthless. Analysts cannot use it for decision-making.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Business Value | 🔴 Critical — core deliverable provides no value |
| User Trust | 🔴 Critical — obvious boilerplate erodes confidence |
| Report Quality | 🔴 Critical — entire deep analysis section is invalid |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/exporters/markdown/company.py` | `generate_deep_analysis()` | Rewrite with signal-based logic |
| `src/solstein/analytics/signals/weakness_detector.py` | New | Extract weaknesses from company data |
| `src/solstein/analytics/signals/opportunity_detector.py` | New | Extract opportunities from company data |
| `tests/unit/test_deep_analysis.py` | New | Test weakness/opportunity extraction |

---

## Dependencies

- **Hard**: STORY-179 (ebitda_margin_pct, recurring_revenue_pct fields) — needed for rich weakness detection
- **Soft**: STORY-173 (threat_level fix) — weakness detection should use correct threat_level
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Create `WeaknessDetector` class in `analytics/signals/` that analyzes a `Company` and returns a list of `Weakness` objects:
```python
@dataclass
class Weakness:
    category: str  # "financial", "operational", "market", "technology"
    severity: str  # "critical", "high", "medium", "low"
    description: str
    evidence: str  # Specific data point triggering this weakness
```

**REQ-2**: Weakness rules (examples):
- `tier == "Tier 4"` → `Weakness("market", "high", "Lowest competitive tier", "Tier 4 classification")`
- `total_funding_raised < 5_000_000` → `Weakness("financial", "high", "Undercapitalized", "€2M funding vs €5M+ peers")`
- `employee_count < 200` → `Weakness("operational", "medium", "Limited execution capacity", "150 employees")`
- `revenue_eur_m < 10` → `Weakness("market", "medium", "Small market presence", "€5M revenue")`
- `profit_margin_pct < 10` → `Weakness("financial", "medium", "Low profitability", "X% margin")`

**REQ-3**: Create `OpportunityDetector` with similar structure for opportunities:
- `recurring_revenue_pct > 80` → `Opportunity("financial", "SaaS revenue model", "85% recurring")`
- `growth_rate_pct > 30` → `Opportunity("growth", "High growth trajectory", "45% CAGR")`
- `ai_maturity in ("Strong", "Very Strong")` → `Opportunity("technology", "AI capabilities", "Strong AI maturity")`

**REQ-4**: Deep analysis template renders actual weaknesses/opportunities, not boilerplate.

---

## Acceptance Criteria

- [ ] Eneve deep analysis shows:
  - Weakness: "Tier 4 — Lowest competitive tier"
  - Weakness: "Undercapitalized — €2M funding"
  - Weakness: "Limited execution capacity — 150 employees"
  - Opportunity: "SaaS revenue model — 85% recurring revenue"
  - Opportunity: "High growth trajectory — 45% CAGR"
  - Opportunity: "AI capabilities — Strong AI maturity"
- [ ] No "No critical weaknesses identified" boilerplate appears
- [ ] Weaknesses are sorted by severity (critical first)
- [ ] Each weakness includes specific evidence from company data
- [ ] Unit tests cover all weakness/opportunity rules

---

## Implementation Note

```python
# weakness_detector.py
class WeaknessDetector:
    RULES = [
        (lambda c: c.tier == "Tier 4", "market", "high", "Lowest competitive tier"),
        (lambda c: c.financials.total_funding_raised < 5_000_000, "financial", "high", "Undercapitalized"),
        # ... more rules
    ]
    
    def detect(self, company: Company) -> list[Weakness]:
        weaknesses = []
        for check, category, severity, description in self.RULES:
            if check(company):
                evidence = self._get_evidence(company, check)
                weaknesses.append(Weakness(category, severity, description, evidence))
        return sorted(weaknesses, key=lambda w: SEVERITY_ORDER[w.severity])
```

---

## Definition of Done

- [ ] `WeaknessDetector` and `OpportunityDetector` implemented
- [ ] Deep analysis report shows actual derived content for Eneve
- [ ] No boilerplate text in generated reports
- [ ] Unit tests for all detector rules
- [ ] Manual verification: report contains specific evidence, not generic statements

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Confirmed via reading deep-analysis.md — all boilerplate |
