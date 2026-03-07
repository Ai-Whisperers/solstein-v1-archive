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
