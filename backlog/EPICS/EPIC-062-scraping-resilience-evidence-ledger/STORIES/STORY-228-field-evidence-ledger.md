# STORY-228: Persist Field-Level Evidence Ledger and Provenance Lineage

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | L (1-2 weeks) |
| **Epic** | EPIC-062 Scraping Resilience and Field Evidence Ledger |
| **Created** | 2026-03-11 |
| **Risk** | High |
| **Assigned** | - |

---

## Audit Verdict

Memory persistence currently stores `latest_report` and `known_urls` per company. It does not preserve complete field-level candidate evidence, winner rationale, or run-to-run lineage in a normalized structure.

---

## Problem Statement

Without a field evidence ledger, the system cannot fully explain why a value won, how it changed over runs, or whether stale values are being reused safely.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Hard to detect stale or low-trust winner values |
| **Maintainability** | Difficult forensic debugging of quality regressions |
| **Compliance** | Limited audit trail for evidence lineage |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/research/ai_research_orchestrator.py` | Modify | Replace flat memory persistence with evidence ledger schema |
| `data/research_results/research_memory.json` | Migrate | Add schema version and ledger sections |
| `scripts/migrate_research_memory_v2.py` | Create | Migration tool with verification output |
| `tests/integration/test_research_memory_schema.py` | Create | Memory schema and migration tests |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- STORY-227

### Soft Dependencies (Preferred Order)
- STORY-229

---

## Architectural Requirements

- **REQ-1**: Memory schema must include schema version, run history, sources, and field-level evidence candidates.
- **REQ-2**: Every non-null final field must reference winning evidence ID(s).
- **REQ-3**: Candidate evidence entries must include source URL, extraction timestamp, confidence, and normalization metadata.
- **REQ-4**: Schema migration must be reversible and validated before overwrite.

---

## Acceptance Criteria

- [ ] `research_memory.json` upgraded to versioned schema with per-company run ledger.
- [ ] Winner lineage available for all non-null output fields.
- [ ] Migration script converts existing memory without data loss.
- [ ] Integration tests pass for migration and subsequent run persistence.
- [ ] Runtime can read old and new schema during migration window.

---

## Definition of Done

### Tests Required
- [ ] Migration round-trip tests (v1 -> v2 -> verify)
- [ ] Integration tests for run append and winner lineage references

### Documentation Required
- [ ] Memory schema v2 spec document
- [ ] Migration runbook and rollback steps

### Code Review Gate
- [ ] Reviewer confirms no silent overwrite path on schema mismatch
- [ ] Reviewer confirms lineage references remain stable across reruns

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Migration bug corrupts memory file | Medium | High | Write to temp file, validate, then atomic replace |
| Ledger growth inflates artifact size | High | Medium | Add retention window and compact mode |

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-03-11 | @opencode | Created |
