# EPIC-062: Scraping Resilience and Field Evidence Ledger

> **Priority**: P0 - Ship Blocker  
> **Stories**: 4 (STORY-226 through STORY-229)  
> **Effort**: L (2-3 weeks)  
> **Dependencies**: EPIC-052 (Provenance, Confidence, and Quality Gates), EPIC-061 (Adaptive Research Planning and Source Intelligence), EPIC-033 (Data Completeness and Export Integrity)  
> **Status**: 🔴 Not Started

---

## Problem

The system now has direct fetch plus fallback and memory reuse, but evidence quality and persistence are still too coarse for reliable long-run intelligence.

Observed in `src/solstein/research/ai_research_orchestrator.py`:

- Page usability checks are improved but not stratified by domain/content strategy.
- Extracted values are merged by confidence, with limited explicit contradiction handling.
- Memory persists latest report and known URLs, but not full field-level evidence lineage.

This creates risk of stale carry-forward, difficult forensic tracing, and weak confidence in financial claims.

---

## Scope

| Category | Action |
|----------|--------|
| Fetch Strategy | Introduce domain/content-type fetch policy matrix with retries and fallbacks |
| Extraction Quality | Add strict extraction contract and unit normalization for numeric fields |
| Evidence Persistence | Persist field-level candidates, winner rationale, and provenance lineage |
| Freshness Policy | Apply field-class freshness windows for reuse/carry-forward decisions |
| Export Trust | Make report/export layers consume field-level evidence and quality tiers |

---

## Stories

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| STORY-226 | Implement domain-aware fetch policy matrix and retry strategy | P0 | M | 🔴 Open |
| STORY-227 | Add extraction contract with unit normalization and contradiction flags | P0 | L | 🔴 Open |
| STORY-228 | Persist field-level evidence ledger and provenance lineage | P0 | L | 🔴 Open |
| STORY-229 | Apply freshness windows and evidence-aware export trust tiers | P1 | M | 🔴 Open |

---

## Target Integration Points

- `src/solstein/research/ai_research_orchestrator.py`
- `src/solstein/cli_ai_research.py`
- `scripts/generate_excel_dashboard.py`
- `data/research_results/research_memory.json`
- `data/research_results/research_results.json`

---

## Architectural Requirements

- **REQ-1**: Fetch behavior must be policy-driven by domain reliability class and content type.
- **REQ-2**: Numeric facts must include normalized unit/currency metadata before synthesis.
- **REQ-3**: Synthesis must preserve candidate evidence and explicit winner rationale per field.
- **REQ-4**: Memory schema must support run history and field-level lineage, not only latest snapshot.
- **REQ-5**: Export/report layers must expose trust tier and evidence sufficiency per company.

---

## Success Criteria

- Blocked/low-value fetch failure rate reduced by >=50% on benchmark low-confidence URL set.
- At least 90% of non-null numeric fields carry unit and currency normalization metadata.
- At least 90% of financial fields in output are either corroborated by >=2 sources or labeled single-source.
- 100% of non-null output fields are traceable to source URL + timestamp + extraction event.
- Export includes trust tiers with explicit quality reasons for every company.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Schema migration complexity for memory | Add versioned schema and migration script with rollback |
| Stricter contracts may drop current coverage | Roll out in warn mode first, then enforce by tier |
| More metadata increases artifact size | Add compact encoding + retention strategy |
| Unit normalization errors introduce bias | Add explicit unknown/ambiguous unit state and tests |

---

## Notes

This epic is the trust and forensic layer. It ensures every value in reports can be explained, challenged, and refreshed without losing historical evidence.
