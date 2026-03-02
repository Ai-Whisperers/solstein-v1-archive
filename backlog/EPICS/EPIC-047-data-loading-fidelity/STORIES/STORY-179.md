# STORY-179: Expose `ebitda_margin_pct` and `recurring_revenue_pct` on `Company` Model

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | M (1 day) |
| **Epic** | EPIC-047 Data Loading Fidelity |
| **Created** | 2026-03-01 |
| **Risk** | Medium — requires domain model change + loader updates + scorer updates |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED DATA LOSS** — verified by live comparison on 2026-03-01.

```
Raw JSON:      "profitability": {"ebitda_margin_pct": 30, "recurring_revenue_pct": 85, ...}
Company obj:   No attributes for these values
```

These fields are nested under `profitability` in the JSON but are not exposed on the `Company` model. They are strong signals for:
- **EBITDA margin (30%)**: Financial health and operational efficiency
- **Recurring revenue (85%)**: SaaS quality and revenue predictability

The `FinancialHealthScorer` could use recurring revenue as a signal for stability. The `GrowthMomentumScorer` could use EBITDA margin as a profitability bonus. Neither can access these values because they don't exist on the Company model.

---

## Problem Statement

The raw JSON contains detailed profitability metrics that the scoring engine cannot see. This is a data loss bug: information is present in the source file but absent from the domain objects that drive scoring and reporting.

The `profitability` object in JSON contains:
- `ebitda_margin_pct` (30)
- `recurring_revenue_pct` (85)
- `revenue_per_employee_eur_k` (333)

Only `revenue_per_employee_eur_k` is currently mapped (to `financials.revenue_per_employee_eur_k`). The other two are lost.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Business Accuracy | 🟠 High — missing key SaaS and profitability signals |
| Scoring Correctness | 🟠 High — 85% recurring revenue is a strong positive signal, not used |
| Report Quality | 🟡 Medium — financial reports could show EBITDA margin and recurring revenue % |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/domain/models.py` | `Company` class | Add `ebitda_margin_pct: Optional[float]` and `recurring_revenue_pct: Optional[float]` |
| `src/solstein/domain/models.py` | `Financials` class (if exists) | Add same fields there |
| `src/solstein/data/loaders.py` | Mapping logic | Map `profitability.ebitda_margin_pct` → `company.ebitda_margin_pct` |
| `src/solstein/data/unified_loader.py` | Same | Same mapping |
| `src/solstein/analytics/scoring.py` | Scorers | Use new fields in scoring formulas |
| `tests/unit/test_domain_models.py` | New | Test new fields |

---

## Dependencies

- **Hard**: Domain model change requires migration consideration (if DB persistence is used)
- **Soft**: STORY-180 (parity test) — once fields are added, parity test verifies mapping
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Add `ebitda_margin_pct: Optional[float] = None` to `Company` model.

**REQ-2**: Add `recurring_revenue_pct: Optional[float] = None` to `Company` model.

**REQ-3**: Map from JSON `profitability.ebitda_margin_pct` → `company.ebitda_margin_pct` in both loaders.

**REQ-4**: Map from JSON `profitability.recurring_revenue_pct` → `company.recurring_revenue_pct` in both loaders.

**REQ-5**: Update `FinancialHealthScorer` to award a small bonus (+0.25) for `recurring_revenue_pct > 80` (strong SaaS signal).

**REQ-6**: Update `GrowthMomentumScorer` to award a small bonus (+0.25) for `ebitda_margin_pct > 25` (strong operational efficiency).

**REQ-7**: Update report templates to display these fields when present.

---

## Acceptance Criteria

- [ ] `Company` model has `ebitda_margin_pct` and `recurring_revenue_pct` attributes
- [ ] `loader.load_companies()[eneve_index].ebitda_margin_pct == 30.0`
- [ ] `loader.load_companies()[eneve_index].recurring_revenue_pct == 85.0`
- [ ] `FinancialHealthScorer` awards +0.25 for recurring_revenue_pct > 80
- [ ] `GrowthMomentumScorer` awards +0.25 for ebitda_margin_pct > 25
- [ ] Financial growth report shows "EBITDA Margin: 30%" and "Recurring Revenue: 85%" for Eneve
- [ ] Unit tests cover new fields and scoring bonuses

---

## Definition of Done

- [ ] Domain model updated with new fields
- [ ] Both loaders updated to map the fields
- [ ] Scorers updated to use the fields
- [ ] Report templates updated to display the fields
- [ ] Unit tests added
- [ ] Manual run: Eneve scores higher than before (due to recurring revenue and EBITDA bonuses)

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Confirmed via raw JSON vs Company object comparison |
