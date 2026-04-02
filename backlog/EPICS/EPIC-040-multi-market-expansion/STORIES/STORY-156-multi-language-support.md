# STORY-156: Multi-Language Support Infrastructure

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-040: Multi-Market Geographic Expansion |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-153, STORY-154 |

## The Strategic Context

> Multi-market expansion requires more than translation — it requires local market intelligence integration.

## Problem Statement

Supporting Dutch, Spanish, and UK markets requires multi-language infrastructure: not just UI translation, but document processing (PDFs in different languages), company name handling (special characters), and LLM prompts that work across languages. This is foundational infrastructure for geographic expansion.

## Impact

| Dimension | Impact |
|-----------|--------|
| **User Experience** | Native language interface |
| **Data Quality** | Proper handling of international text |
| **Scalability** | Foundation for future markets |

## Affected Files

| File | Issue |
|------|-------|
| `dashboard/` | No internationalization framework |
| `llm/` | No multi-language prompt handling |

## Architectural Requirements

- i18n framework: react-i18next for dashboard, Python gettext for backend
- Language detection: auto-detect document language, handle mixed-language sources
- Character encoding: UTF-8 throughout, handle special characters (Dutch ij, Spanish ñ, etc.)
- LLM handling: prompts that work across languages, translation where needed
- Document processing: OCR for Dutch/Spanish documents, proper text extraction
- Company name normalization: handle international naming conventions
- Right-to-left support: foundation for future Arabic/Hebrew markets (optional but architected)
- Regional variants: Dutch (NL vs. BE), Spanish (ES vs. LATAM), English (UK vs. US)

## Acceptance Criteria

- [ ] i18n framework implemented in dashboard
- [ ] Dutch and Spanish translations complete
- [ ] Document processing handles international text
- [ ] LLM prompts work across languages
- [ ] Company names display correctly with special characters

## Definition of Done

- **Tests Required**: Multi-language UI and document processing tests
- **Documentation Required**: Internationalization guide for developers
- **Code Review Gate**: Reviewer verifies no hardcoded English strings remain

## Notes

Infrastructure for global expansion, not just translation.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
